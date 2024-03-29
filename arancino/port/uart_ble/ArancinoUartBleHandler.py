# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 SmartMe.IO

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

#from adafruit_ble.services.nordic import UARTService
from .ArancinoUartBleService import ArancinoUartBleService

from arancino.ArancinoConstants import *
from arancino.utils.ArancinoUtils import *
from arancino.port.ArancinoPort import PortTypes
import time
from msgpack import Unpacker

LOG = ArancinoLogger.Instance().getLogger()

class ArancinoUartBleHandler(threading.Thread):

    def __init__(self, conn, id, device, commandReceivedHandler, connectionLostHandler):

        self.__name = "{}-{}".format(self.__class__.__name__, id)

        threading.Thread.__init__(self, name=self.__name)
        self.__conn = conn  # the uart service of the uart-ble port        
        self.__service = self.__conn[ArancinoUartBleService]
        self.__id = id
        self.__device = device
        self.__log_prefix = "[{} - {} at {}]".format(PortTypes(PortTypes.UART_BLE).name, self.__id, self.__device)

        self.__commandReceivedHandler = commandReceivedHandler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connectionLostHandler = connectionLostHandler  # handler to be called when a connection is lost or stopped

        self.__stop = False


    def run(self):
        time.sleep(1.5)  # do il tempo ad Arancino di inserire la porta in lista
        unpacker = Unpacker()
        #self.__service.reset_input_buffer()
        #self.__service.write(b'\n')
        while not self.__stop:
            # Ricezione dati
            try:

                # Read bytes one by one
                data_size = self.__service.in_waiting

                if data_size > 0:

                    data = self.__service.read(data_size)

                    unpacker.feed(data)
                
                for raw_cmd in unpacker:
                    self.__commandReceivedHandler(raw_cmd)


            except Exception as ex:
                # probably some I/O problem such as disconnected port
                LOG.error("{}I/O Error while reading data from {} port: {}".format(self.__log_prefix, PortTypes(PortTypes.UART_BLE).name, str(ex)))

                self.__stop = True
                break

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