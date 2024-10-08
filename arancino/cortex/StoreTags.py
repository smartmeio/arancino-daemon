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
from arancino.ArancinoConstants import SUFFIX_TMSTP, SUFFIX_TAG, SUFFIX_LBL
from redis.exceptions import RedisError
from datetime import datetime

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()


class StoreTags(CortexCommandExecutor):

    # region Store Example
    '''
    {
        "C": "5",
        "A":{
            "K": "<key-1>",
            "I": [
                {"N": "<tag-1>", "V": "<value-1>"},
                {"N": "<tag-2>", "V": "<value-2>"}
            ],
            "TS": "<UNIX timestamp>"
        },
        "CF":{
            "A": 1,
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

            # region Selezione del datastore

            datastore = self._datastore_tag

            items = self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.ITEMS]
            port_id = self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.PORT_ID]
            ts = self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.ITEM.TIMESTAMP]
            key = self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.ITEM.KEY]

            for i in items:
                tag = i[self.PACKET.CMD.ARGUMENTS.ITEM.TAG]
                val = i[self.PACKET.CMD.ARGUMENTS.ITEM.VALUE]

                saved_tags =[]
                d_key = "{}:{}:{}:{}".format(port_id, key, SUFFIX_TAG, tag)
                if datastore.exists(d_key):
                    saved_tags = datastore.lrange(d_key, 0, -1)

                if not len(saved_tags) or val != saved_tags[1]:
                    datastore.lpush(d_key, val)
                    datastore.lpush(d_key, ts)

            #endregion

            #region Creo la Response

            self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK
            self._createChallenge()

            #endregion

            return self.arancinoResponse

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    def _check(self):
        """
        esegui controlli sui parametri della comando STORETAGS.
        """
        #region CFG:ACK
        # controllo se il paramentro ack è presente e valido, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT) \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] < 0 \
                or self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] > 1:
            self.arancinoCommand.cfg[self.PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:ACK Missing or Incorret: set default value ack:1"))
        #endregion

        #region ARGS:TS
        if not self._checkKeyAndValue(self.arancinoCommand.args, self.PACKET.CMD.ARGUMENTS.TIMESTAMP) \
                or self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.TIMESTAMP].strip() == "":
            self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.TIMESTAMP] = str(int(datetime.now().timestamp() * 1000))
        #endregion

        #region ARGS:ITEMS
        if not self._checkKeyAndValue(self.arancinoCommand.args, self.PACKET.CMD.ARGUMENTS.ITEMS) \
                or len(self.arancinoCommand.args[self.PACKET.CMD.ARGUMENTS.ITEMS]) == 0:
            raise ArancinoException("Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty", ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        #endregion
