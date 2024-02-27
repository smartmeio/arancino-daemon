# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2022 SmartMe.IO

Authors:  Sergio Tomasello <sergio@smartme.io>

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License
"""


from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.cortex.ArancinoPacket import PCK, ArancinoCommand, ArancinoResponse
from abc import ABC, abstractmethod

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()

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
    def log_prexix(self):
        return ""


    @property
    def PACKET(self):
        return self.__packet


    @PACKET.setter
    def PACKET(self, PACKET: str):
        self.__packet = PACKET


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


    # region Utilities
    def _createChallenge(self):
        """
        Quando è presente il secure mode, genera la challange,
        la aggancia all'Arancino Response ritorna.
        :return:
        """

        if self.PACKET.CMD.CONFIGURATIONS.SIGNATURE in self.arancinoCommand.cfg:
            sign = self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.SIGNATURE]
            chlng = ""  # TODO
            self.arancinoResponse.cfg[self.PACKET.RSP.CONFIGURATIONS.CHALLENGE] = chlng


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

            if value is not None:
                return True
            else:
                return False
        else:
            return False


    def _retrieveDatastore(self):
        # datastore standard di default
        datastore = self._datastore

        if self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.TYPE] == self.PACKET.CMD.CONFIGURATIONS.TYPES.APPLICATION:

            if self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PERSISTENT] == 1:
                datastore = self._datastore_pers
            else:
                datastore = self._datastore

        elif self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.TYPE] == self.PACKET.CMD.CONFIGURATIONS.TYPES.RESERVED:
            datastore = self._datastore_rsvd

        elif self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.TYPE] == self.PACKET.CMD.CONFIGURATIONS.TYPES.SETTING:
            datastore = self._datastore_stng
        
        elif self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.TYPE] == self.PACKET.CMD.CONFIGURATIONS.TYPES.TIMESERIES:
            datastore = self._datastore_tser

        elif self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.TYPE] == self.PACKET.CMD.CONFIGURATIONS.TYPES.TSTAGS:
            datastore = self._datastore_tag
        

        return datastore


    # endregion

'''
class CortexCommandExecutorFactory:

    def __init__(self):
        self.commands = {
            "START": Start,
            "GET": arancino.cortex.Get.Get

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
'''

'''
class Start(CortexCommandExecutor):

    #region Start Example
    """
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
    """
    #endregion

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand
        self.arancinoResponse = ArancinoResponse(packet=None)


    def execute(self):
        try:
            self._check()

            #region Creo la Response

            self.arancinoResponse.cfg[PACKET.RSP.CONFIGURATIONS.TIMESTAMP] = str(int(datetime.now().timestamp() * 1000))
            self.arancinoResponse.cfg[PACKET.RSP.CONFIGURATIONS.LOG_LEVEL] = CONF.get_log_level()

            self.arancinoResponse.args[PACKET.RSP.ARGUMENTS.DAEMON_VERSION] = str(CONF.get_metadata_version())
            self.arancinoResponse.args[PACKET.RSP.ARGUMENTS.DAEMON_ENVIRONMENT] = CONF.get_general_env()

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
        self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
        #endregion

        #region CFG:SCR_MOD
        """
        imposto di default il parametro secure mode ad 0
        """
        self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.SECURE_MODE] = 0
        #endregion

        #region ARGS:
        """
        verifico che ci si siano tutti i campi obbligatori, se ne manca
        anche solo uno, sollevo eccezione.
        """

        if not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.FIRMWARE.NAME) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.FIRMWARE.VERSION) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.FIRMWARE.MCU_FAMILY) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.FIRMWARE.LIBRARY_VERSION) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.FIRMWARE.CORE_VERSION) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.FIRMWARE.BUILD_TIME) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.FIRMWARE.CORTEX_VERSION) \
                or not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.PORT_ID):

            raise ArancinoException("Arguments Error: One or more mandatory arguments are missing or empty. Please check.", ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        else:
            # TODO Debug log "Command Integrity Check: Passed
            pass
        #endregion
'''
"""
"START": Start
"SIGN": Sign,
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
"""