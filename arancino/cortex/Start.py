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

from arancino.ArancinoConstants import ArancinoCommandResponseCodes, ArancinoCommandErrorCodes
from arancino.ArancinoExceptions import ArancinoException
from arancino.cortex.CortexCommandExectutor import CortexCommandExecutor
from arancino.cortex.ArancinoPacket import ArancinoCommand, ArancinoResponse
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment
from arancino.cortex.ArancinoPacket import PACKET
from datetime import datetime


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
ENV = ArancinoEnvironment.Instance()

class Start(CortexCommandExecutor):

    #region Start Example
    '''
        {
        "C": "0",
        "A":{
            "P": "<port unique identified>",
            "FMF": "<mcu family>",
            "FLV": "<firmware library version>",
            "FN": "<firmware name>",
            "FW": "<firmware version>",
            "FBT": "<firmware build time>",
            "FCV": "<firmware core version>",
            "FXV": "<firmware cortex version>",
            "CUSTOM_KEY_1": "CUSTOM_VALUE_1",
            "CUSTOM_KEY_2": "CUSTOM_VALUE_2"
        },
        "CF":{
            "SM": "<secure mode>",
            "CS": "<Signer Certificate>",
            "CD": "<Device Certificate>"
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

            self.arancinoResponse.cfg[PACKET.RSP.CONFIGURATIONS.TIMESTAMP] = str(int(datetime.now().timestamp() * 1000))
            self.arancinoResponse.cfg[PACKET.RSP.CONFIGURATIONS.LOG_LEVEL] = CONF.get("log").get("level")

            self.arancinoResponse.args[PACKET.RSP.ARGUMENTS.DAEMON_VERSION] = str(ENV.version)
            self.arancinoResponse.args[PACKET.RSP.ARGUMENTS.DAEMON_ENVIRONMENT] = ENV.env

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
