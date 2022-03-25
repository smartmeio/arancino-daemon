
from abc import ABC, abstractmethod

from redis.exceptions import RedisError

from arancino.ArancinoConstants import ArancinoCommandErrorCodes, ArancinoCommandResponseCodes, ArancinoSpecialChars
from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.ArancinoExceptions import *
from arancino.ArancinoPacket import *
from datetime import datetime
import msgpack

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()

#TODO usare semver
DAEMON_CORTEX_VERSION = "1.0.0"

class CortexCommandExecutor(ABC):


        # Redis Data Stores
    redis = ArancinoDataStore.Instance()
    _datastore = redis.getDataStoreStd()
    _datastore_rsvd = redis.getDataStoreRsvd()
    _devicestore = redis.getDataStoreDev()
    _datastore_pers = redis.getDataStorePer()
    _datastore_tser = redis.getDataStoreTse()
    _datastore_tag = redis.getDataStoreTag()
    _datastore_stng = redis.getDataStoreStng()


    @property
    def arancinoCommand(self):
        return self.__arancinoCommand


    @arancinoCommand.setter
    def arancinoCommand(self, arancinoCommand: ArancinoCommand):
        self.__arancinoCommand = arancinoCommand


    @property
    def arancinoResponse(self):
        return self.__arancinoResponse


    @arancinoResponse.setter
    def arancinoResponse(self, arancinoResponse: ArancinoResponse):
        self.__arancinoResponse = arancinoResponse


    @abstractmethod
    def execute(self) -> ArancinoResponse:
        pass


    @abstractmethod
    def _check(self):
        pass

    def getUnpackedPacket(self):
        pass


    def getPackedPacket(self):
        pass

    #region Utilities
    def _createChallenge(self) -> str:
        """
        Quando è presente il secure mode, genera la challange,
        la aggancia all'Arancino Response ritorna.
        :return:
        """

        if PACKET.CONFIGURATIONS.SIGNATURE in self.arancinoCommand.cfg:
            sign = self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.SIGNATURE]
            chlng = "" #TODO
            self.arancinoResponse.cfg[PACKET.CONFIGURATIONS.CHALLENGE] = chlng



    def _checkKeyAndValue(self, dict: dict, key: str) -> bool:
        """
        Verifica che la chiave sia presente nel dizionario
            ed anche valorizzata
        :param key: (str) la chiave da verificare
        :param dict: (dict) il dizionare in cui controllare

        :return True/False: (bool)
        """

        if key in dict:
            value = dict[key]

            if value:
                return True
            else:
                return False
        else:
            return False


    def _retrieveDatastore(self):
        # datastore standard di default
        datastore = self._datastore

        if self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.TYPE] == PACKET.CONFIGURATIONS.TYPES.APPLICATION:

            if self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.PERSISTENT] == 1:
                datastore = self._datastore_pers
            else:
                datastore = self._datastore

        elif self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.TYPE] == PACKET.CONFIGURATIONS.TYPES.RESERVED:
            datastore = self._datastore_rsvd

        elif self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.TYPE] == PACKET.CONFIGURATIONS.TYPES.SETTING:
            datastore = self._datastore_stng

        return datastore

    #endregion

class CortexCommandExecutorFactory:

    def __init__(self):
        self.commands = {
            "START": Start,
            "SET": Set,
            "GET": Get,
            "DEL": Del,
            "HSET": HashSet,
            "HGET": HashGet,
            "HDEL": HashDel,
            "PUB": Publish,
            "FLUSH": Flush,
            "STORE": Store,
            "STORETAGS": StoreTags,
        }

    def getCommandExecutor(self, cmd: ArancinoCommand) -> CortexCommandExecutor:

        if cmd:

            if isinstance(cmd, ArancinoCommand):

                if cmd.id in self.commands:
                    # uso un dizionario per trovare il Cortex Command per l'Arancino Command
                    # passato (usando l'id). Questo evita di fare uno switch case statement.
                    ccmd = self.commands[cmd.id]

                    # istanzio un Cortex Command, passando l'Arancino Command
                    ccmd = ccmd(arancinoCommand=cmd)

                    return ccmd

                else:
                    raise InvalidCommandException("Command does not exist: [{}] - Skipped".format(cmd.id), ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)
            else:
                """ 
                se non è dei tipi di cui sopra allora è un tipo sconosciuto 
                e genero una eccezione.
                """

                raise InvalidCommandException("Invalid Command type/format - Skipped", ArancinoCommandErrorCodes.ERR_CMD_TYPE)
        else:
            raise InvalidCommandException("Invalid Command (None) - Skipped", ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)


class Start(CortexCommandExecutor):

    #region Start Example
    '''
        {
        "cmd": "START",
        "args":{
            "port_id": "<port unique identified>",
            "fw_mcu_family": "<mcu family>",
            "fw_lib_ver": "<firmware library version>",
            "fw_name": "<firmware name>",
            "fw_ver": "<firmware version>",
            "fw_build_time": "<firmware build time>",
            "fw_core_ver": "<firmware core version>",
            "fw_crtx_ver": "<firmware cortex version>",
            "CUSTOM_KEY_1": "CUSTOM_VALUE_1",
            "CUSTOM_KEY_2": "CUSTOM_VALUE_2"
        },
        "cfg":{
            "crt_sig": "<Signer Certificate>",
            "crt_dev": "<Device Certificate>"
        }
    }
    '''
    #endregion

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand
        self.arancinoResponse = ArancinoResponse(packet=None)


    def execute(self):
        try:
            self._check()

            #region Creo la Response

            self.arancinoResponse.cfg[PACKET.CONFIGURATIONS.TIMESTAMP] = str(int(datetime.now().timestamp() * 1000))
            self.arancinoResponse.cfg[PACKET.CONFIGURATIONS.LOG_LEVEL] = CONF.get_log_level()

            self.arancinoResponse.args[PACKET.ARGUMENTS.DAEMON_VERSION] = str(CONF.get_metadata_version())
            self.arancinoResponse.args[PACKET.ARGUMENTS.DAEMON_ENVIRONMENT] = CONF.get_general_env()

            self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK

            self._createChallenge()
            #endregion

            return self.arancinoResponse

        except ArancinoException as ex:
            raise ex

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)


    def _check(self):
        """
        esegui controlli sui parametri del comando START.
        """

        #region CFG:ACK
        """
        imposto di default il parametro ack ad 1 perche nella start ci si 
        deve sempre aspettare qualcosa indietro.
        """
        self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
        #endregion

        #region CFG:SCR_MOD
        """
        imposto di default il parametro secure mode ad 0
        """
        self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.SECURE_MODE] = 0
        #endregion

        #region ARGS:
        """
        verifico che ci si siano tutti i campi obbligatori, se ne manca
        anche solo uno, sollevo eccezione.
        """

        if not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.FIRMWARE.NAME) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.FIRMWARE.VERSION) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.FIRMWARE.MCU_FAMILY) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.FIRMWARE.LIBRARY_VERSION) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.FIRMWARE.CORE_VERSION) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.FIRMWARE.BUILD_TIME) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.FIRMWARE.CORTEX_VERSION) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.PORT_ID):

            raise ArancinoException("Arguments Error: One or more mandatory arguments are missing or empty. Please check.", ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        else:
            # TODO Debug log "Command Integrity Check: Passed
            pass
        #endregion

class Sign(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand
        self.arancinoResponse = ArancinoResponse(packet=None)

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando SIGN.
        """
        pass


class Set(CortexCommandExecutor):

    # region Set Example
    '''
        {
            "cmd": "SET",
            "args": {
                "items":[
                    {"key": "<key>", "value": "<value>"}
                ]
            },
            "cfg":{
                "type": "appl",
                "pers": 1,
                "ack": 1,
                "sgntr": "<Signature>"
            }
        }
    '''
    #endregion

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand
        self.arancinoResponse = ArancinoResponse(packet=None)

    def execute(self):

        try:
            self._check()

            # region Selezione del datastore in base al paramentro "type"

            datastore = self._retrieveDatastore()

            items = self.arancinoCommand.args[PACKET.ARGUMENTS.ITEMS]

            map = {}

            for i in items:
                key = i["key"]
                val = i["value"]
                map[key] = val

            dts_rsp = datastore.mset(map)
            #endregion

            #region Creo la Response

            #per ottimizzazioni creo la risposta solo se è richiesto
            if self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.ACKNOLEDGEMENT] == 1:
                if dts_rsp:
                    # code OK
                    self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK
                else:
                    # code ERROR
                    self.arancinoResponse.code = ArancinoCommandErrorCodes.ERR_NULL

                self._createChallenge()

            #endregion

            return self.arancinoResponse

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    def _check(self):
        """
        esegui controlli sui parametri della comando SET.
        """

        #region CFG:PERSISTENT
        # controllo se il paramentro di persistenza è presente, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, PACKET.CONFIGURATIONS.PERSISTENT) \
                or self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.PERSISTENT] < 0 \
                or self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.PERSISTENT] > 1:
            self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.PERSISTENT] = 0
        #endregion

        #region CFG:ACK
        # controllo se il paramentro ack è presente e valido, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, PACKET.CONFIGURATIONS.ACKNOLEDGEMENT) \
                or self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.ACKNOLEDGEMENT] < 0 \
                or self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.ACKNOLEDGEMENT] > 1:
            self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
        #endregion

        #region ARGS:ITEMS
        if not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.ITEMS) \
                or len(self.arancinoCommand.args[PACKET.ARGUMENTS.ITEMS]) == 0:
            raise ArancinoException("Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty", ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        #endregion



class Get(CortexCommandExecutor):

    #region Get Example
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
    #endregion

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        try:
            self._check()

            # region Selezione del datastore in base al paramentro "type"

            keys = self.arancinoCommand.args[PACKET.ARGUMENTS.ITEMS]

            datastore = self._retrieveDatastore()

            if self.arancinoCommand.cfg[PACKET.CONFIGURATIONS.TYPE] == PACKET.CONFIGURATIONS.TYPES.APPLICATION:

                """
                TYPE: APPL
                trattandosi di chiavi applicative, possono essere sia volatili che persistenti
                percui prima cerco sul datastore volatile (default, in quanto il parametro "pers"
                non è specificato nella Get), qualora non ci fosse nel datastore volatile, chiave 
                per chiave cerco nel datastore persistente. Se anche li la chiave non è trovata, 
                sarà valorizzata a None
                """
                values = datastore.mget(keys)


                datastore = self._datastore_pers # Cambio Datastore passando al persistente

                for idx, val in enumerate(values):
                    if val is None:
                        # check if key exists in persistent datastore:
                        chk = datastore.get(keys[idx])
                        if chk is None:
                            values[idx] = None
                        else:
                            values[idx] = chk
            else:

                """
                TYPE: RSVD o STNG
                il datastatore in questo caso è obbligato dal tipo.
                """
                values = datastore.mget(keys)

            #endregion

            #region Creo la Response

            items = []
            self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK

            for idx, val in enumerate(values):
                item = {"key": keys[idx], "value": values[idx]}
                items.append(item)

            self.arancinoResponse.args[PACKET.ARGUMENTS.ITEMS] = items

            self._createChallenge()

            #endregion

            return self.arancinoResponse

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    def _check(self):
        """
        esegui controlli sui parametri della comando GET.
        """

        #region ARGS:ITEMS
        if not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.ARGUMENTS.ITEMS) \
                or len(self.arancinoCommand.args[PACKET.ARGUMENTS.ITEMS]) == 0:
            raise ArancinoException("Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty", ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        #endregion



class Store(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando STORE.
        """
        pass


class StoreTags(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando STORETAGS.
        """
        pass


class HashSet(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando HSET.
        """
        pass


class HashGet(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando HGET.
        """
        pass


class Del(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando DEL.
        """
        pass


class HashDel(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando HDEL.
        """
        pass


class Publish(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando PUB.
        """
        pass


class Flush(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando FLUSH.
        """
        pass


    """
    class CMD:
    ARGS = ARGUMENTS
    CFG = CONFIGURATION
    """




class PACKET:

    CONFIGURATION = "cfg"
    ARGUMENT = " args"
    RESPONSE_CODE = "code"
    COMMAND_ID = "cmd"

    class ARGUMENTS:

        ITEMS = "items"
        KEYS = "keys"
        PORT_ID = "port_id"

        DAEMON_VERSION = "dmn_ver"
        DAEMON_ENVIRONMENT = "dmn_env"

        class FIRMWARE:

            MCU_FAMILY = "fw_mcu_family"
            LIBRARY_VERSION = "fw_lib_ver"
            NAME = "fw_name"
            VERSION = "fw_ver"
            BUILD_TIME = "fw_build_time"
            CORE_VERSION = "fw_core_ver"
            CORTEX_VERSION = "fw_crtx_ver"


    class CONFIGURATIONS:

        SIGNATURE = "sgntr"
        CHALLENGE = "chlng"

        SIGNER_CERTIFICATE = "crt_sig"
        DEVICE_CERTIFICATE = "dev_sig"

        TIMESTAMP = "ts"
        LOG_LEVEL = "log_lvl"
        SECURE_MODE = "scr_mod"

        PERSISTENT = "pers"
        ACKNOLEDGEMENT = "ack"
        TYPE = "type"

        class TYPES:

            APPLICATION = "appl"
            SETTING = "stng"
            RESERVED = "rsvd"

if __name__ == '__main__':

    cmd_get = {
        "cmd": "GET",
        "args": {
            "items": [
                {"key": "<key>", "value": "<value>"}
            ]
        },
        "cfg": {
            "type": "appl",
            "pers": 0,
            "ack": 1,
            "sgntr": "<signature>"
        }
    }

    cmd_start = {
        "cmd": "START",
        "args": {
            "port_id": "<port unique identified>",
            "fw_mcu_family": "<mcu family>",
            "fw_lib_ver": "<firmware library version>",
            "fw_name": "<firmware name>",
            "fw_ver": "<firmware version>",
            "fw_build_time": "<firmware build time>",
            "fw_core_ver": "<firmware core version>",
            "fw_crtx_ver": "<cortex version>",
            "CUSTOM_KEY_1": "CUSTOM_VALUE_1",
            "CUSTOM_KEY_2": "CUSTOM_VALUE_2"
        },
        "cfg": {
            "crt_sig": "<Signer Certificate>",
            "crt_dev": "<Device Certificate>"
        }
    }

    pck = cmd_start

    pck_pack = msgpack.packb(pck, use_bin_type=True)

    acmd2_0 = ArancinoCommand(packet=pck)
    acmd2_1 = ArancinoCommand(packet=pck_pack)
    acmd2_2 = ArancinoCommand(packet=None)


    factory = CortexCommandExecutorFactory()

    cmd1 = factory.getCommandExecutor(cmd=acmd2_0)
    cmd2 = factory.getCommandExecutor(cmd=acmd2_1)


    print(cmd1.arancinoCommand.getUnpackedPacket())
    print(cmd2.arancinoCommand.getUnpackedPacket())


    rsp1 = cmd1.execute()
    rsp2 = cmd2.execute()


    print(rsp1.getUnpackedPacket())
    print(rsp2.getUnpackedPacket())


