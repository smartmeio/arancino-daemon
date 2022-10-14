from redis.exceptions import RedisError

from arancino.ArancinoConstants import ArancinoCommandResponseCodes, ArancinoCommandErrorCodes
from arancino.ArancinoExceptions import ArancinoException, RedisGenericException
from arancino.cortex.CortexCommandExectutor import CortexCommandExecutor
from arancino.cortex.ArancinoPacket import ArancinoCommand, ArancinoResponse
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.cortex.ArancinoPacket import PACKET

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()


class Get(CortexCommandExecutor):
    # region Get Example
    '''
        {
            "cmd": "GET",
            "args":{
                "items":[
                    "<key-1>", "<key-2>", "<key-n>"
                ]
            },
            "cfg":{
                "type": "appl",
                "sgntr": "<Signature>"
            }
        }
    '''

    # endregion

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand
        self.arancinoResponse = ArancinoResponse(packet=None)

    def execute(self):
        try:
            self._check()

            keys = self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.ITEMS]
            # region Selezione del datastore in base al paramentro "type"
            datastore = self._retrieveDatastore()
            """
            TYPE: APPL
            il database viene selezionato il base al parametro di configurazione pers.

            TYPE: RSVD o STNG
            il datastatore in questo caso è obbligato dal tipo.
            """

            values = datastore.mget(keys)

            # endregion

            # region Creo la Response

            items = []
            self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK

            for idx, val in enumerate(values):
                item = {"key": keys[idx], "value": values[idx]}
                items.append(item)

            self.arancinoResponse.args[PACKET.RSP.ARGUMENTS.ITEMS] = items

            self._createChallenge()

            # endregion

            return self.arancinoResponse

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    def _check(self):
        """
        esegui controlli sui parametri della comando GET.
        """

        # region CFG:PERSISTENT
        # controllo se il paramentro di persistenza è presente, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, PACKET.CMD.CONFIGURATIONS.PERSISTENT) \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PERSISTENT] < 0 \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PERSISTENT] > 1:
            self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PERSISTENT] = 0
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:PERS Missing or Incorret: set default value pers:0"))
        # endregion

        # region CFG:ACK
        # im questo caso, qualsiasi sia il valore di ack lo imposto di default a 1, perche la funzioni tipo get
        # devono tornare sempre il dato.
        self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
        # endregion

        # region ARGS:ITEMS
        if not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.ITEMS) \
                or len(self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.ITEMS]) == 0:
            raise ArancinoException(
                "Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty",
                ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        # endregion
