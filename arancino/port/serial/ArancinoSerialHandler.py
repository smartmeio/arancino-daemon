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
from arancino.utils.ArancinoUtils import *
from arancino.port.ArancinoPort import PortTypes
from queue import Queue
import time
import timeit

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg

class ArancinoSerialHandler(threading.Thread):

    def __init__(self, name, serial, id, device, commandReceivedHandler, connectionLostHandler):
        threading.Thread.__init__(self, name=name)
        self.__serial_port = serial      # the serial port
        self.__name = name          # the name, usually the arancino port id
        self.__id = id
        self.__device = device
        self.__log_prefix = "[{} - {} at {}]".format(PortTypes(PortTypes.SERIAL).name, self.__id, self.__device)

        self.__commandReceivedHandler = commandReceivedHandler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connectionLostHandler = connectionLostHandler    # handler to be called when a connection is lost or stopped

        self.__partial_command = ""
        self.__partial_bytes_command = bytearray(b'')
        self.__stop = False

        self.__cmd_queue = Queue(maxsize = CONF.get('port').get('serial').get('queue_max_size'))
        self.__th_cmd_executor = threading.Thread(target = self.__exec_cmd)
        self.__th_cmd_executor.start()


    def run(self):
        time.sleep(1.5)  # do il tempo ad Arancino di inserire la porta in lista
        count = 0
        str_data = ""
        while not self.__stop:
            # Ricezione dati
            try:
                
                self.__partial_bytes_command = self.__serial_port.read(self.__serial_port.in_waiting or 1)
                
                try:

                    self.__cmd_queue.put(self.__partial_bytes_command)
                    #LOG.error("QUEUE LENGTH:  {}".format(self.__cmd_queue.qsize()))
                except Exception as ex:

                    LOG.error("{}Error while appending data from serial port to queue: {}".format(self.__log_prefix, str(ex)))
                




            except Exception as ex:
                # probably some I/O problem such as disconnected USB serial
                LOG.error("{}I/O Error while reading data from serial port: {}".format(self.__log_prefix, str(ex)))

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

    def __exec_cmd(self):
        line = b''
        try:
            while not self.__stop:
                try:
                    if not self.__cmd_queue.empty():
                        line += self.__cmd_queue.get()
                        while b'\x04' in line:
                            var, line = line.split(b'\x04', 1)
                        
                            try:
                                var = var.decode('utf-8', errors='strict')

                            except UnicodeDecodeError as ex:
                                LOG.warning("{}Decode Warning while reading data from serial port: {}".format(self.__log_prefix, str(ex)))
                                #line = line.decode('utf-8', errors='backslashreplace')

                            if self.__commandReceivedHandler is not None:
                                start3 = timeit.default_timer()
                                self.__commandReceivedHandler(var)
                                stop3 = timeit.default_timer()
                                #LOG.warning(f"TOTAL TIME EXECUTION: {stop3 - start3}")
                                #time.sleep(.1)

                        #LOG.warning(f"QUEUE LENGHT OUT WHILE: {self.__cmd_queue.qsize()}")
                except Exception as ex:
                    LOG.error("{}CMD execution failed: {}".format(self.__log_prefix, str(ex)))
                
        except Exception as ex:
            LOG.error("{}Dequeue thread failed: {}".format(self.__log_prefix, str(ex)))


    def stop(self):
        self.__stop = True