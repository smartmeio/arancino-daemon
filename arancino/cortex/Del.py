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
from arancino.ArancinoExceptions import ArancinoException, RedisGenericException
from arancino.cortex.CortexCommandExectutor import CortexCommandExecutor
from arancino.cortex.ArancinoPacket import ArancinoCommand, ArancinoResponse
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.cortex.ArancinoPacket import PCK
from redis.exceptions import RedisError

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()

class Del(CortexCommandExecutor):

    # region Del Example
    '''
        {
            "C": "3",
            "A": {
                "I":[
                    "<key-1>", "<key-2>", "<key-n>"
                ]
            },
            "CF":{
                "A": 0,
                "P": 1,
                "PX": 1,
                "SGN": "<Signature>"
            }
        }
    '''
    #endregion

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand
        self.PACKET = PCK.PACKET[arancinoCommand.cortex_version]
        self.arancinoResponse = ArancinoResponse(packet=None, cortex_version=arancinoCommand.cortex_version)

    def execute(self):
        try:
            self._check()

            datastore = self._retrieveDatastore()

            items = self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.ITEMS]

            # esegue un cambio di nome delle chiavi qualora il prefix id fosse abilitato
            items = self._prefix(items)

            res = datastore.delete(*items)

            # region Creo la Response

            self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK
            self.arancinoResponse.args[self.PACKET.RSP.ARGUMENTS.KEYS] = int(res)

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
        esegui controlli sui parametri della comando DEL.
        """
        # region CFG:TYPE
        # forzo il tipo applicativo
        self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.TYPE] = self.PACKET.CMD.CONFIGURATIONS.TYPES.APPLICATION
        # endregion

        # region CFG:PERSISTENT
        # controllo se il paramentro di persistenza è presente, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, self.PACKET.CMD.CONFIGURATIONS.PERSISTENT) \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PERSISTENT] < 0 \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PERSISTENT] > 1:
            self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.PERSISTENT] = 0
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:PERS Missing or Incorret: set default value pers:0"))
        # endregion

        # region CFG:ACK
        # controllo se il paramentro ack è presente e valido, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT) \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] < 0 \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] > 1:
            self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:ACK Missing or Incorret: set default value ack:1"))
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
