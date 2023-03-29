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
import decimal

from arancino.ArancinoConstants import ArancinoCommandResponseCodes, ArancinoCommandErrorCodes
from arancino.ArancinoExceptions import ArancinoException, RedisGenericException
from arancino.cortex.CortexCommandExectutor import CortexCommandExecutor
from arancino.cortex.ArancinoPacket import ArancinoCommand, ArancinoResponse
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment
from arancino.cortex.ArancinoPacket import PACKET
from arancino.ArancinoConstants import SUFFIX_TMSTP
from redis.exceptions import RedisError

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
ENV = ArancinoEnvironment.Instance()


class Store(CortexCommandExecutor):


    # region Store Example
    '''
        "cmd": "STORE",
        "args":{
            "items":[
                {"key": "key-1", "value": "value-1", "ts": "timestamp-1"},
                {"key": "key-2", "value": "value-2", "ts": "timestamp-2"},
                {"key": "key-3", "value": "value-3", "ts": "timestamp-3"},
                {"key": "...", "value": "...", "ts": "..."}
            ]
        },
        "cfg":{
            "ack": 1,
            "appl": "tse"
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

            # region Selezione del datastore

            datastore = self._retrieveDatastore()            

            items = self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.ITEMS]
            #prefix_id = self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PREFIX_ID]
            port_id = self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.PORT_ID]
            ts_items = []

            for i in items:
                key = "{}:{}".format(port_id, i["key"])

                self._check_ts_exist_and_create(datastore, key)

                val = float(decimal.Decimal(i["value"]))
                ts = "*" if "ts" not in i or i["ts"].strip() == "" else i["ts"]

                datastore.ts().add(key, ts, val)
                ts_items.append(ts)

            #endregion

            #region Creo la Response

            self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK
            self.arancinoResponse.args[PACKET.RSP.ARGUMENTS.ITEMS] = ts_items
            self._createChallenge()

            #endregion

            return self.arancinoResponse

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)


    def _check(self):
        """
        esegui controlli sui parametri del comando STORE.
        """
        #region CFG:ACK
        # controllo se il paramentro ack è presente e valido, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT) \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] < 0 \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] > 1:
            self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] = 1
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:ACK Missing or Incorret: set default value ack:1"))
        #endregion

        # # region CFG:PRFX
        # # controllo se il paramentro prfx è presente e valido, altrimenti lo imposto di default
        # if not self._checkKeyAndValue(self.arancinoCommand.cfg, PACKET.CMD.CONFIGURATIONS.PREFIX_ID) \
        #         or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PREFIX_ID] < 0 \
        #         or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PREFIX_ID] > 1:
        #     self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PREFIX_ID] = 0
        #     LOG.debug("{} - {}".format(self.log_prexix, "CFG:PRFX Missing or Incorret: set default value prfx:0"))
        # # endregion

        #region ARGS:ITEMS
        if not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.ITEMS) \
                or len(self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.ITEMS]) == 0:
            raise ArancinoException("Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty", ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        #endregion


    def _check_ts_exist_and_create(self, datastore, key):

        exist = datastore.exists(key)

        if not exist:
            labels = {
                # "device_id": self.__conf.get_serial_number(),
                "port_id": self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.PORT_ID],
                "port_type": self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.PORT_TYPE],
            }

            if not ENV.serial_number == "0000000000000000" and not ENV.serial_number== "ERROR000000000":
                labels["device_id"] = ENV.serial_number

            datastore.ts().create(key, labels=labels, duplicate_policy='last', retention_msecs=CONF.get("redis").get("retetion"))
            datastore.set("{}:{}".format(key, SUFFIX_TMSTP), 0)  # Starting timestamp
