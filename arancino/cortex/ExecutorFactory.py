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

from arancino.ArancinoConstants import ArancinoCommandErrorCodes
from arancino.ArancinoExceptions import InvalidCommandException

from arancino.cortex.Start import Start
from arancino.cortex.Set import Set
from arancino.cortex.Get import Get
from arancino.cortex.Del import Del
from arancino.cortex.Store import Store
from arancino.cortex.StoreTags import StoreTags
from arancino.cortex.HashSet import HashSet
from arancino.cortex.HashGet import HashGet
from arancino.cortex.HashDel import HashDel
from arancino.cortex.Publish import Publish
from arancino.cortex.Flush import Flush
from arancino.cortex.Sign import Sign

from arancino.cortex.CortexCommandExectutor import CortexCommandExecutor
from arancino.cortex.ArancinoPacket import ArancinoCommand


class CortexCommandExecutorFactory:

    def __init__(self):
        self.commands_100 = {
            "START": Start,
            "GET": Get,
            "SET": Set,
            "DEL": Del,
            "HSET": HashSet,
            "HGET": HashGet,
            "HDEL": HashDel,
            "FLUSH": Flush,
            "STORE": Store,
            "STORETAGS": StoreTags,
            "PUB": Publish,
            "SIGN": Sign
        }

        self.commands_110 = {
            "0": Start,
            "1": Set,
            "2": Get,
            "3": Del,
            "4": Store,
            "5": StoreTags,
            "6": HashSet,
            "7": HashGet,
            "8": HashDel,
            "9": Publish,
            "10": Flush,
            "11": Sign
        }

        self.commands = self.commands_110

    def getCommandExecutor(self, cmd: ArancinoCommand) -> CortexCommandExecutor:

        if cmd:

            if isinstance(cmd, ArancinoCommand):

                if str(cmd.id) in self.commands_110:
                    self.commands = self.commands_110
                elif str(cmd.id) in self.commands_100:
                    self.commands = self.commands_100
                else:
                    raise InvalidCommandException("Command does not exist: [{}] - Skipped".format(cmd.id), ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)

                # uso un dizionario per trovare il Cortex Command per l'Arancino Command
                # passato (usando l'id). Questo evita di fare uno switch case statement.
                ccmd = self.commands[str(cmd.id)]

                # istanzio un Cortex Command, passando l'Arancino Command
                ccmd = ccmd(arancinoCommand=cmd)

                return ccmd


            else:
                """ 
                se non è dei tipi di cui sopra allora è un tipo sconosciuto 
                e genero una eccezione.
                """

                raise InvalidCommandException("Invalid Command type/format - Skipped",
                                              ArancinoCommandErrorCodes.ERR_CMD_TYPE)
        else:
            raise InvalidCommandException("Invalid Command (None) - Skipped", ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)
