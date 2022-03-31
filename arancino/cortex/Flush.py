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
from arancino.cortex.ArancinoPacket import PACKET
from redis.exceptions import RedisError

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()

class Flush(CortexCommandExecutor):

    # region HashDel Example
    '''
    {
        "cmd": "FLUSH",
        "args":{},
        "cfg":{
            "pers": 0,
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

            datastore = self._retrieveDatastore()

            res = datastore.flushdb()

            # region Creo la Response

            if res is not None:
                if res:
                    self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK
                else:
                    self.arancinoResponse.code = ArancinoCommandResponseCodes.ERR_REDIS
            else:
                raise RedisError

            self._createChallenge()

            # endregion

            return self.arancinoResponse

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)


    def _check(self):
        """
        esegui controlli sui parametri della comando HDEL.
        """
        # region CFG:TYPE
        # forzo il tipo applicativo
        self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.TYPE] = PACKET.CMD.CONFIGURATIONS.TYPES.APPLICATION
        # endregion

        # region CFG:PERSISTENT
        # controllo se il paramentro di persistenza è presente, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, PACKET.CMD.CONFIGURATIONS.PERSISTENT) \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PERSISTENT] < 0 \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PERSISTENT] > 1:
            self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PERSISTENT] = 0
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:PERS Missing or Incorret: set default value pers:0"))
        # endregion

        # region CFG:ACK
        # controllo se il paramentro ack è presente e valido, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT) \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] < 0 \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] > 1:
            self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:ACK Missing or Incorret: set default value ack:1"))
        # endregion