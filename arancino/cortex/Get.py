from redis.exceptions import RedisError

from arancino.ArancinoConstants import ArancinoCommandResponseCodes, ArancinoCommandErrorCodes
from arancino.ArancinoExceptions import ArancinoException, RedisGenericException
from arancino.cortex.CortexCommandExectutor import CortexCommandExecutor
from arancino.cortex.ArancinoPacket import ArancinoCommand, ArancinoResponse
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.cortex.ArancinoPacket import PCK

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()


class Get(CortexCommandExecutor):
    # region Get Example
    '''
        {
            "C": "2",
            "A":{
                "I":[
                    "<key-1>", "<key-2>", "<key-n>"
                ]
            },
            "CF":{
                "P": 1,
                "T": "A",
                "PX": 0,
                "SGN": "<Signature>"
            }
        }
    '''

    # endregion

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand
        self.PACKET = PCK.PACKET[arancinoCommand.cortex_version]
        self.arancinoResponse = ArancinoResponse(packet=None, cortex_version=arancinoCommand.cortex_version)


    def execute(self):
        try:
            self._check()

            keys = self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.ITEMS]
            prefix_id = self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PREFIX_ID]
            port_id = self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.PORT_ID]

            # region Selezione del datastore in base al paramentro "type"
            datastore = self._retrieveDatastore()
            """
            TYPE: APPL
            il database viene selezionato il base al parametro di configurazione pers.

            TYPE: RSVD o STNG
            il datastatore in questo caso è obbligato dal tipo.
            """

            # esegue un cambio di nome delle chiavi qualora il prefix id fosse abilitato
            keys_w_prefix = self._prefix(keys)

            values = datastore.mget(keys_w_prefix)

            # endregion

            # region Creo la Response

            items = []
            self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK

            for idx, val in enumerate(values):
                item = {"key": keys[idx], "value": values[idx]}
                items.append(item)

            self.arancinoResponse.args[self.PACKET.RSP.ARGUMENTS.ITEMS] = items

            self._createChallenge()

            # endregion

            return self.arancinoResponse

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)


    def _prefix(self, keys):
        prefix_id = self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PREFIX_ID]
        port_id = self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.PORT_ID]

        if int(prefix_id) == 1:
            """
            il comando usa il prefix id, per cui a tutte le chiavi va agganciato l'id della porta. 
            """

            # istanza di comodo da usare qualora il prefix_id fosse attivo.
            keys_prfx = []

            for k in keys:
                k = "{}_{}".format(port_id, k)
                keys_prfx.append(k)

            return keys_prfx

        else:
            """
            il comando non usa il prefix id 
            """
            return keys


    def _check(self):
        """
        esegui controlli sui parametri della comando GET.
        """

        # region CFG:PERSISTENT
        # controllo se il paramentro di persistenza è presente, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, self.PACKET.CMD.CONFIGURATIONS.PERSISTENT) \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PERSISTENT] < 0 \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PERSISTENT] > 1:
            self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PERSISTENT] = 0
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:PERS Missing or Incorret: set default value pers:0"))
        # endregion

        # region CFG:ACK
        # im questo caso, qualsiasi sia il valore di ack lo imposto di default a 1, perche la funzioni tipo get
        # devono tornare sempre il dato.
        self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
        # endregion

        # region CFG:PRFX
        # controllo se il paramentro prfx è presente e valido, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, self.PACKET.CMD.CONFIGURATIONS.PREFIX_ID) \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PREFIX_ID] < 0 \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PREFIX_ID] > 1:
            self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PREFIX_ID] = 0
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:PRFX Missing or Incorret: set default value prfx:0"))
        # endregion

        # region ARGS:ITEMS
        if not self._checkKeyAndValue(self.arancinoCommand.args, self.PACKET.CMD.ARGUMENTS.ITEMS) \
                or len(self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.ITEMS]) == 0:
            raise ArancinoException(
                "Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty",
                ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        # endregion
