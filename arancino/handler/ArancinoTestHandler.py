# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2020 SmartMe.IO

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

import threading
from arancino.ArancinoConstants import *
from arancino.ArancinoUtils import *
from arancino.port.ArancinoPort import PortTypes
from arancino.ArancinoCortex import ArancinoCommandIdentifiers as cmdId
from arancino.ArancinoConstants import ArancinoSpecialChars as specChars
from random import randrange
import time

LOG = ArancinoLogger.Instance().getLogger()

class ArancinoTestHandler(threading.Thread):

    def __init__(self, name, id, device, commandReceivedHandler, connectionLostHandler):
        threading.Thread.__init__(self,name=name)

        self.__name = name          # the name, usually the arancino port id
        self.__id = id
        self.__device = device
        self.__log_prefix = "[{} - {} at {}]".format(PortTypes(PortTypes.TEST).name, self.__id, self.__device)

        self.__commandReceivedHandler = commandReceivedHandler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connectionLostHandler = connectionLostHandler    # handler to be called when a connection is lost or stopped

        self.__stop = False

        self.__command_test_list = self.__getCommnandsList()

    def run(self):
        commands_test_num = len(self.__command_test_list)
        count = 0

        if commands_test_num > 0:
            while not self.__stop:
                # Ricezione dati
                try:


                    raw_cmd = self.__command_test_list[count]

                    # send back the raw command
                    if self.__commandReceivedHandler is not None:
                        self.__commandReceivedHandler(raw_cmd)

                    if count == commands_test_num-1:
                        count = 0  # reset the counter and start again
                    else:
                        count += 1  # go to the next command

                    time.sleep(randrange(3))

                except Exception as ex:
                    # probably some I/O problem such as disconnected USB serial
                    LOG.error("{}I/O Error while reading data from test port: {}".format(self.__log_prefix, str(ex)))

                    self.__stop = True
                    break
            else:
                LOG.warning("{}No commands list defined for test port.".format(self.__log_prefix))


        self.__connection_lost()


    def __connection_lost(self):
        '''
        When a connection_lost is triggered means the connection to the serial port is lost or interrupted.
        In this case ArancinoPort (from plugged_ports) must be updated and status information stored into
        the device store.
        '''
        try:

            LOG.warning("{}Connection lost".format(self.__log_prefix))
            if self.__connectionLostHandler is not None:
                self.__connectionLostHandler()

        except Exception as ex:
            LOG.exception("{}Error on connection lost: {}".format(self.__log_prefix, str(ex)))

    def stop(self):
        self.__stop = True



    def __getCommnandsList(self):
        list = []
        list.append(cmdId.CMD_SYS_START["id"] + specChars.CHR_SEP + "0.0.1" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_SET["id"] + specChars.CHR_SEP + "TEST_KEY" + specChars.CHR_SEP + "TEST_VAL" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_SET_PERS["id"] + specChars.CHR_SEP + "TEST_PERS_KEY" + specChars.CHR_SEP + "TEST_PERS_VAL" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_GET["id"] + specChars.CHR_SEP + "TEST_KEY" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_GET["id"] + specChars.CHR_SEP + "TEST_PERS_KEY" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_KEYS["id"] + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

        # TODO: add all command to test
        return list

