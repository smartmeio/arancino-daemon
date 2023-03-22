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


class HashGet(CortexCommandExecutor):
    # region HashGet Example
    '''
    {
        "cmd": "HGET",
        "args":{
            "items":[
                {"key": "<key-1>", "field": "<field-A>"},
                {"key": "<key-1>", "field": "<field-B>"},
                {"key": "<key-2>", "field": "<field-C>"}
            ]
        },
        "cfg":{
            "type": "appl",
            "prfx": 1,
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

            items = self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.ITEMS]
            prefix_id = self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PREFIX_ID]
            port_id = self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.PORT_ID]

            # region Selezione del datastore in base al paramentro "type"
            datastore = self._retrieveDatastore()
            """
            TYPE: APPL
            il database viene selezionato il base al parametro di configurazione pers.

            TYPE: RSVD o STNG
            il datastatore in questo caso è obbligato dal tipo.
            """

            for i in items:
                k = i["key"]
                f = i["field"]

                if int(prefix_id) == 1:
                    """
                    il comando usa il prefix id, per cui a tutte le chiavi va agganciato l'id della porta. 
                    """
                    k_w_prfx = "{}_{}".format(port_id, k)

                    v = datastore.hget(k_w_prfx, f)

                else:
                    """
                    il comando non usa il prefix id 
                    """
                    v = datastore.hget(k, f)

                i["value"] = v

            # endregion

            # region Creo la Response

            self.arancinoResponse.code = ArancinoCommandResponseCodes.RSP_OK
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
        esegui controlli sui parametri della comando HGET.
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

        # region CFG:PRFX
        # controllo se il paramentro prfx è presente e valido, altrimenti lo imposto di default
        if not self._checkKeyAndValue(self.arancinoCommand.cfg, PACKET.CMD.CONFIGURATIONS.PREFIX_ID) \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PREFIX_ID] < 0 \
                or self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PREFIX_ID] > 1:
            self.arancinoCommand.cfg[PACKET.CMD.CONFIGURATIONS.PREFIX_ID] = 0
            LOG.debug("{} - {}".format(self.log_prexix, "CFG:PRFX Missing or Incorret: set default value prfx:0"))
        # endregion

        # region ARGS:ITEMS
        if not self._checkKeyAndValue(self.arancinoCommand.args, PACKET.CMD.ARGUMENTS.ITEMS) \
                or len(self.arancinoCommand.args[PACKET.CMD.ARGUMENTS.ITEMS]) == 0:
            raise ArancinoException(
                "Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty",
                ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)
        # endregion
