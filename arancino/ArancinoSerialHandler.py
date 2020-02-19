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
from arancino.ArancinoCortex import ArancinoComamnd
from arancino.ArancinoConstants import *
from arancino.ArancinoUtils import *

LOG = ArancinoLogger.Instance().get_logger()

class ArancinoSerialHandler(threading.Thread):

    def __init__(self, name,  serial, id, device, command_received_handler, connection_lost_handler):
        threading.Thread.__init__(self)
        self.__serial = serial      # the serial port
        self.__name = name          # the name, usually the arancino port id
        self.__id = id
        self.__device = device
        self.__log_prefix = "[" + self.__id + " => " + self.__device + "] "

        self.__command_received_handler = command_received_handler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connection_lost_handler = connection_lost_handler    # handler to be called when a connection is lost or stopped

        self.__partial_command = ""
        self.__stop = False


    def run(self):
        count = 0
        str_data = ""
        while not self.__stop:
            # Ricezione dati
            try:

                # Read bytes one by one
                data = self.__serial.read(1)

                data_dec = data.decode()
                self.__partial_command += data_dec

                if self.__partial_command.endswith(ArancinoSpecialChars.CHR_EOT) is True:
                    # now command is completed and can be used

                    # send back the raw command
                    self.__command_received_handler(self.__partial_command)

                    # clear the handy variable and start again
                    self.__partial_command = ""


            except Exception as ex:
                # probably some I/O problem such as disconnected USB serial
                LOG.exception("{}I/O Error while reading data from serial port: {}".format(self.__log_prefix, str(ex)))

                self.__stop = True

        self.__connection_lost()


    def __connection_lost(self):
        '''
        When a connection_lost is triggered means the connection to the serial port is lost or interrupted.
        In this case ArancinoPort (from plugged_ports) must be updated and status information stored into
        the device store.
        '''
        try:

            LOG.warning("{}Connection lost".format(self.__log_prefix))
            self.__connection_lost_handler()

        except Exception as ex:
            LOG.exception("{}Error on connection lost: {}".format(self.__log_prefix, str(ex)))

    def stop(self):
        self.__stop = True