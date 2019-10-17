# coding=utf-8
'''
SPDX-license-identifier: Apache-2.0

Copyright (c) 2018 SmartMe.IO

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
'''

import signal
import sys
import time
from datetime import timedelta

from serial.threaded.__init__ import *

import arancino.arancino_conf as conf
import arancino.arancino_constants as const
from arancino.arancino_datastore import ArancinoDataStore
from arancino.arancino_exceptions import InvalidArgumentsNumberException, InvalidCommandException, RedisGenericException, NonCompatibilityException
from arancino.arancino_port import ArancinoPortsDiscovery
from arancino.arancino_synch import ArancinoSynch


class Arancino():

    def __init__(self):
        try:
            self.init()

        except Exception as ex:
            LOG.error(str(ex))
            exit(1)


    def init(self):
        try:

            '''
            global commands_list, ports_plugged, ports_connected, arancinoDs, arancinoSy, arancinoDy
            
            commands_list = const.getCommandsList()
            ports_plugged = {}
            ports_connected = {}

            arancinoDs = ArancinoDataStore()
            arancinoSy = ArancinoSynch()
            arancinoDy = ArancinoPortsDiscovery()
            '''

            self.serialMonitor = SerialMonitor("Aranncino-SerialMonitor")

        except Exception as ex:
            LOG.error(str(ex))
            exit(1)


    def start(self):

        self.serialMonitor.start()
        signal.signal(signal.SIGINT, self.__exit)
        signal.signal(signal.SIGTERM, self.__exit)


    def stop(self):
        LOG.info("Received Stop: Exiting... ")
        self.serialMonitor.stop()


    def __exit(self, signum, frame):
        LOG.warning("Received Kill: Exiting... ")
        self.serialMonitor.stop()



class SerialMonitor (threading.Thread):

    kill_now = False
    arancinoContext = None

    ports_connected = {}
    ports_plugged = {}

    arancinoDs = None
    arancinoDy = None
    arancinoSy = None

    def __init__(self, name):

        super(SerialMonitor, self).__init__()
        self._stop_event = threading.Event()

        self.arancinoDs = ArancinoDataStore()
        self.arancinoSy = ArancinoSynch(self.arancinoDs)
        self.arancinoDy = ArancinoPortsDiscovery()

        self.datastore = self.arancinoDs.getDataStore()
        #probably is not necessary to flush when starts, becouse it's clean when the device is started
        #self.datastore.flushdb()
        self.datastore.set(const.RSVD_KEY_MODVERSION, conf.version)

        self.devicestore = self.arancinoDs.getDeviceStore()
        self.datastore_rsvd = self.arancinoDs.getDataStoreRsvd()


        self.arancinoContext = {
            "commands_list": const.getCommandsList(),
            "reserved_keys_list" : const.getReservedKeysList(),
            "ports_plugged": self.ports_plugged,
            "ports_connected": self.ports_connected,
            "arancino_discovery": self.arancinoDy,
            "arancino_synch": self.arancinoSy,
            "arancino_datastore": self.arancinoDs,
            "compatibility_array" : const.COMPATIBILITY_MATRIX_MOD[conf.version]
        }



    # public function
    def stop(self):
        self.kill_now = True

    # private function, makes the real stop. invoked by the thread.
    def __stop(self):
        ''' EXIT PROCEDURE START'''
        LOG.debug("Closing Redis Connection...")

        self.datastore.connection_pool.disconnect()
        self.devicestore.connection_pool.disconnect()

        LOG.info("Redis Connection Closed")
        LOG.debug("Closing Serial Ports Connection...")

        # Close each serial connection
        to_stop = []
        for id, p_connected in self.ports_connected.items():
            # ports_plugged[id]
            arancino = self.ports_plugged[id]
            to_stop.append(arancino)

        if to_stop is not None and len(to_stop) > 0:
            self.__stopPorts(to_stop, self.ports_plugged, self.ports_connected)


        #set Plugged and Connected Metadata to False in every PORT in devicestore
        self.arancinoSy.synchPorts(self.ports_plugged)

        LOG.info("Serial Ports Connection Closed")
        LOG.info("Exiting completed, Bye!")

        self._stop_event.set()
        sys.exit(0)

    def run(self):
        # Polls every 10 seconds if there's new serial port to connect to

        thread_start = time.time()
        thread_start_reset = time.time()

        while not self.kill_now:

            self.ports_plugged = self.arancinoDy.getPluggedArancinoPorts(self.ports_plugged, self.ports_connected)

            #LOG.info("Plugged Serial Ports Retrieved: " + str(len(self.ports_plugged)))
            LOG.debug('Plugged Serial Ports Retrieved: ' + str(len(self.ports_plugged)) + ' => ' + ' '.join('[' + str(arancino.port.device) + ' - ' + str(key) + ']'for key, arancino in self.ports_plugged.items()))

            #LOG.info("Connected Serial Ports: " + str(len(self.ports_connected)))
            LOG.debug('Connected Serial Ports: ' + str(len(self.ports_connected)) + ' => ' + ' '.join('[' + str(connector.arancino.port.device) + ' - ' + str(key) + ']' for key, connector in self.ports_connected.items()))

            #log that every hour
            if (time.time()-thread_start_reset) >= 3600:
                LOG.info('Plugged Serial Ports Retrieved: ' + str(len(self.ports_plugged)) + ' => ' + ' '.join('[' + str(arancino.port.device) + ' - ' + str(key) + ']' for key, arancino in self.ports_plugged.items()))
                LOG.info('Connected Serial Ports: ' + str(len(self.ports_connected)) + ' => ' + ' '.join('[' + str(connector.arancino.port.device) + ' - ' + str(key) + ']' for key, connector in self.ports_connected.items()))
                LOG.info('Uptime: ' + str(timedelta(seconds=int(time.time() - thread_start))))
                thread_start_reset = time.time()

            # first synchronization in cycle
            self.arancinoSy.synchPorts(self.ports_plugged)


            #retrieve if there are new ports to connect to - is a list of type Serial.Port
            if self.ports_plugged:
                ports_to_connect = self.__retrieveNewPorts(self.ports_plugged, self.ports_connected)
                #LOG.info("Connectable Serial Ports Retrieved: " + str(len(ports_to_connect)))
                LOG.debug("Connectable Serial Ports Retrieved: " + str(len(ports_to_connect)) + ' => ' + ' '.join('[' + str(p.port.device) + ' - ' + str(p.id) + ']' for p in ports_to_connect))

                #finally connect the new ports
                if ports_to_connect:
                    self.__connectPorts(ports_to_connect, self.ports_connected)


            to_stop = self.__getDisabledPorts(self.ports_plugged, self.ports_connected)
            if to_stop is not None and len(to_stop) > 0:
                self.__stopPorts(to_stop, self.ports_plugged, self.ports_connected)


            # second synchronization in cycle
            self.arancinoSy.synchPorts(self.ports_plugged)

            time.sleep(conf.cycle_time)

        self.__stop()

    def __retrieveNewPorts(self, plugged, connected):
        """
        Retrieves new ports to connect to.
        Starting from plugged ports, it checks if a port is contained inside
        the list of connected ports. It also checks if the port is enabled
        and can be connected.

        :param plugged: Dict of ArancinoPorts
        :param connected: List of SerialConnector which rappresents the connected ports
        :return: List of ArancinoPorts to connect to
        """

        ports_to_connect = []

        try:
            for id, arancino in plugged.items():
                if arancino.id not in connected:
                        if arancino.enabled:
                            # if true: there'are new plugged ports discovered
                            ports_to_connect.append(arancino)
                        else:
                            LOG.warning("Port Not Enabled: " + arancino.alias + " " + arancino.port.device + " - " + arancino.id)

        except Exception as ex:
            LOG.exception(ex)

        return ports_to_connect


    def __connectPorts(self, ports_to_connect, connected):
        """
        For each ports in List, creates a new instance of Serial Connector and starts it.
        Serial Connector instance is stored into a List of connected port using the
        serial number of the port as key for the List

        :param ports_to_connect: List of ArancinoPort
        :return ports_connected: List of SerialConnector and SerialTransport
        """

        try:

            for arancino in ports_to_connect:
                LOG.info("Connecting to Port: " + arancino.alias + " " + arancino.port.device + " - " + arancino.id)

                #serialConnector = SerialConnector( self.datastore, self.devicestore,  arancino=arancino, baudrate = 4000000)
                serialConnector = SerialConnector(self.arancinoContext, arancino=arancino, baudrate=4000000)


                serialConnector.start()
                #connected[arancino.id] = [serialConnector, None]  # SerialConnector and SerialTransport
                connected[arancino.id] = serialConnector
                arancino.connected = True

        except Exception as ex:
            LOG.exception(ex)

    def __getDisabledPorts(self, plugged, connected):
        """
        Cycles all the connected ports and puts the disabled ones into
        disabled_ports List. Finally it returns disabled_ports

        :param connected: Dict of Connected Ports
        :param plugged: Dict of Plugged Ports
        :return disabled_ports: a list of Disabled ArancinoPort

        """
        disabled_ports = []


        try:
            for id, conn_arr in connected.items():
                arancino = plugged[id]
                if arancino is not None and not arancino.enabled:
                    disabled_ports.append(arancino)

        except Exception as ex:
            LOG.exception(ex)

        return disabled_ports


    def __stopPorts(self, ports_to_stop, plugged, connected):
        """
        Cycles all the connected ports and puts the disabled ones into
        disabled_ports List. Finally it returns disabled_ports

        :param connected: Dict of Connected Ports
        :param plugged: Dict of Plugged Ports

        """
        try:
            for arancino in ports_to_stop:
                connector = connected[arancino.id]
                #todo da capire come gestire il transport
                #transport = port[const.IDX_SERIAL_TRANSPORT]
                #transport.close()

                #connector = port[const.IDX_SERIAL_CONNECTOR]
                #connector = port
                connector.close()

                arancino.connected = False
                arancino.plugged = (arancino.id in self.arancinoDy.getPluggedArancinoPorts(plugged, connected))

                # if id in connected:
                #     port = connected.pop(arancino.id)
                #     del port

                del connector
                #del transport
                LOG.info("Port Closed: " + arancino.alias + " " + arancino.port.device + " - " + arancino.id)

        except Exception as ex:
            LOG.exception(ex)


class ArancinoLineReader(LineReader):

    def write(self, text):
        self.transport.write(text.encode(self.ENCODING, self.UNICODE_HANDLING))


# class ArancinoReaderThread(ReaderThread):
#
#     # def __init__(self):
#     #     super.__init__(daemon=True)
#
#     def run(self):
#         """Reader loop"""
#         if not hasattr(self.serial, 'cancel_read'):
#             self.serial.timeout = 1
#         self.protocol = self.protocol_factory()
#         try:
#             self.protocol.connection_made(self)
#         except Exception as e:
#             self.alive = False
#             self.protocol.connection_lost(e)
#             self._connection_made.set()
#             return
#         error = None
#         self._connection_made.set()
#         while self.alive and self.serial.is_open:
#             try:
#                 # read all that is there
#                 data = self.serial.read(self.serial.in_waiting)
#             except serial.SerialException as e:
#                 # probably some I/O problem such as disconnected USB serial
#                 # adapters -> exit
#                 error = e
#                 break
#             else:
#                 if data:
#                     # make a separated try-except for called user code
#                     try:
#                         self.protocol.data_received(data)
#                     except Exception as e:
#                         error = e
#                         break
#         self.alive = False
#         self.protocol.connection_lost(error)
#         self.protocol = None


class SerialConnector:

    def __init__(self, arancinoContext, arancino, baudrate=250000):

        self.arancino = arancino
        self.log_prefix = "[" + self.arancino.port.device + " - " + self.arancino.id + "]: "
        try:

            self.name = "ArancinoSerialConnector-" + self.arancino.port.device
            self.baudrate = baudrate

            self.arancinoContext = arancinoContext
            #self.datastore = arancinoContext["arancino_datastore"].getDataStore()
            #self.devicestore = arancinoContext["arancino_datastore"].getDeviceStore()
            self.serial = serial.serial_for_url(self.arancino.port.device, baudrate=self.baudrate, timeout=None)
            #self.arancinoReaderTh = ArancinoReaderThread(self.serial, lambda: SerialHandler(self.arancinoContext, self.arancino))

            self.arancinoReaderTh = ReaderThread(self.serial, lambda: SerialHandler(self.arancinoContext, self.arancino))

        except Exception as ex:
            LOG.exception(self.log_prefix + str(ex))

    def close(self):
        try:
            '''
            Close the serial is enough becouse in the run() of ReaderThread there's this control:
                ===> while self.alive and self.serial.is_open
            exiting the while it calls the .join() and close the thread
            '''
            self.arancinoReaderTh.serial.close()

        except Exception as ex:
            LOG.exception(self.log_prefix + str(ex))

    def start(self):
        try:
            self.arancinoReaderTh.start()
        except Exception as ex:
            LOG.exception(self.log_prefix + str(ex))


class SerialHandler(ArancinoLineReader):

    def __init__(self, arancinoContext, arancino=None):

        self.arancinoContext = arancinoContext
        self.datastore = arancinoContext["arancino_datastore"].getDataStore()
        self.devicestore = arancinoContext["arancino_datastore"].getDeviceStore()
        self.datastore_rsvd = arancinoContext["arancino_datastore"].getDataStoreRsvd()
        self.ports_connected = arancinoContext["ports_connected"]
        self.ports_plugged = arancinoContext["ports_plugged"]
        self.arancinoSy = arancinoContext["arancino_synch"]
        self.arancinoDy = arancinoContext["arancino_discovery"]
        self.arancinoDs = arancinoContext["arancino_datastore"]
        self.commands_list = arancinoContext["commands_list"]
        self.reserved_keys_list = arancinoContext["reserved_keys_list"]
        self.compatibility_array = arancinoContext["compatibility_array"]

        self.arancino = arancino

        self._partial = ""
        self.log_prefix = "[" + self.arancino.port.device + " - " + self.arancino.id + "]: "

    def connection_made(self, transport):
        try:
            super(SerialHandler, self).connection_made(transport)
            self.transport = transport
            LOG.info(self.log_prefix + "Port opened: " + transport.serial.name)
            LOG.debug(self.log_prefix + "Port opened: " + str(transport))
            transport.serial.rts = False
            #todo verificare la gestioen dell'oggetto transport

            #self.ports_connected[self.arancino.id][const.IDX_SERIAL_TRANSPORT] = transport
        except Exception as ex:
            LOG.exception(self.log_prefix + str(ex))

    def connection_lost(self, exc):
        '''
        When a connection_lost is triggered means the connection to the serial port is lost or interrupted.
        In this case ArancinoPort (from plugged_ports) must be updated and status information stored into
        the device store.
        '''
        try:
            # sets connected metadata status to False.
            self.arancino.connected = False

            # using arancino discovery utility, gets the the all plugged ports and the check if the current arancino port is
            # plugged or not, if yes plugged metadata status is True, otherwise, False
            self.arancino.plugged = (self.arancino.id in self.arancinoDy.getPluggedArancinoPorts(self.ports_plugged, self.ports_connected))

            # call arancino synch utility to synchronize with the datastore.
            self.arancinoSy.synchPort(self.arancino)

            LOG.info(self.log_prefix + "Port closed " + self.transport.serial.name)
            LOG.debug(self.log_prefix + "Port closed " + str(self.transport))

            connected_port = self.ports_connected.pop(self.arancino.id)
            #serial_connector = connected_port[const.IDX_SERIAL_CONNECTOR]
            #serial_connector = connected_port
            #serial_transport = connected_port[const.IDX_SERIAL_TRANSPORT]

            #todo verificare se è corretto commentare la transporto.close()e anche verificare l'oggetto serial_transport
            #serial_transport.close()
            #serial_connector.close()
            connected_port.close()

            #del serial_transport
            #del serial_connector
            del connected_port

        except Exception as ex:
            LOG.exception(self.log_prefix + str(ex))


    def data_received(self, data):

        #print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        datadec = data.decode()
        self._partial += datadec

        if self._partial.endswith(const.CHR_EOT) is True:
            # now command is completed and can be used
            LOG.debug(self.log_prefix + "Received Command: " + self._partial.strip('\n').strip('\t'))

            try:
                # parse and check command
                cmd = self.__parseCommands(self._partial)
                # then execute it
                response = self.__execCommand(cmd)

            except NonCompatibilityException as ex:
                LOG.error(self.log_prefix + str(ex) + " => " + self._partial)
                response = ex.error_code + const.CHR_EOT

            except InvalidArgumentsNumberException as ex:
                LOG.error(self.log_prefix + str(ex) + " => " + self._partial)
                response = ex.error_code + const.CHR_EOT

            except InvalidCommandException as ex:
                LOG.warning(self.log_prefix + str(ex) + " => " + self._partial)
                response = ex.error_code + const.CHR_EOT

            except RedisGenericException as ex:
                LOG.error(self.log_prefix + str(ex) + " => " + self._partial)
                response = ex.error_code + const.CHR_EOT

            except Exception as ex:
                LOG.error(self.log_prefix + str(ex))
                response = const.ERR + const.CHR_EOT

            finally:
                # send response back
                #self.transport.write(response.encode())
                self.write(response)

                LOG.debug(self.log_prefix + "Sent Response: " + str(response))


            # clear the handy variable
            self._partial = ""

            LOG.debug('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')

        else:
            LOG.debug('Partial Command Received: ' + datadec.strip('\n').strip('\t'))

    def __parseCommands(self, command):
        #decode the received commands
        #cmd = command.decode().strip()

        #splits command by separator char
        cmd = command.strip(const.CHR_EOT).split(const.CHR_SEP)

        if len(cmd) > 0:
            if cmd[0] in self.commands_list:
                #comando presente
                return cmd
            else:
                raise InvalidCommandException("Command does not exist: " + cmd[0] + " - Skipped", const.ERR_CMD_NOT_FND)
        else:
            raise InvalidCommandException("No command received", const.ERR_CMD_NOT_RCV)

        return cmd

    def __execCommand(self, cmd):

        idx = len(cmd)
        parameters = cmd[1:idx]
        try:
            # START
            if cmd[0] == const.CMD_SYS_START:
                return self.__OPTS_START(parameters)
            # SET
            elif cmd[0] == const.CMD_APP_SET_STD:
                return self.__OPTS_SET_STD(parameters)
            # SET PERSISTENT
            elif cmd[0] == const.CMD_APP_SET_PERS:
                return self.__OPTS_SET_PERS(parameters)
            # GET
            elif cmd[0] == const.CMD_APP_GET:
                return self.__OPTS_GET(parameters)
            # DEL
            elif cmd[0] == const.CMD_APP_DEL:
                return self.__OPTS_DEL(parameters)
            # KEYS
            elif cmd[0] == const.CMD_APP_KEYS:
                return self.__OPTS_KEYS(parameters)
            # HSET
            elif cmd[0] == const.CMD_APP_HSET:
                return self.__OPTS_HSET(parameters)
            # HGET
            elif cmd[0] == const.CMD_APP_HGET:
                return self.__OPTS_HGET(parameters)
            # HGETALL
            elif cmd[0] == const.CMD_APP_HGETALL:
                return self.__OPTS_HGETALL(parameters)
            # HKEYS
            elif cmd[0] == const.CMD_APP_HKEYS:
                return self.__OPTS_HKEYS(parameters)
            # HVALS
            elif cmd[0] == const.CMD_APP_HVALS:
                return self.__OPTS_HVALS(parameters)
            # HDEL
            elif cmd[0] == const.CMD_APP_HDEL:
                return self.__OPTS_HDEL(parameters)
            # PUB
            elif cmd[0] == const.CMD_APP_PUB:
                return self.__OPTS_PUB(parameters)
            # FLUSH
            elif cmd[0] == const.CMD_APP_FLUSH:
                return self.__OPTS_FLUSH(parameters)
            # Default
            else:
                return const.ERR_CMD_NOT_FND + const.CHR_SEP

        except Exception as ex:
            # generic error handler which raise back exception
            raise ex

    # START
    def __OPTS_START(self, args):
        '''
        Microcontroller sends START command to start communication

        MCU → START@

        MCU ← 100@ (OK)
        '''

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:
            
            # first argument in the START comamnd is the version of the library
            value_libvers = args[0]
            key_libvers = const.RSVD_KEY_LIBVERSION + self.arancino.id + const.RSVD_CHARS

            # store the reserved key
            self.datastore.set(key_libvers, value_libvers)

            # and then check if it's compatible. if the library is not compatible, disconnect the board and 
            if value_libvers not in self.compatibility_array:
                # TODO disconnect the device. If the device is not disconnected, it will try to START every 2,5 seconds.
                raise NonCompatibilityException("Module version " + conf.version + " can not work with Library version " + value_libvers + " on the device: " + self.arancino.port.device + " - " + self.arancino.id, const.ERR_NON_COMPATIBILITY)
            
            else:
                return const.RSP_OK + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException("Invalid arguments number for command " + const.CMD_SYS_START + ". Received: " + str(n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)


    # SET STANDARD (to standard device store)
    def __OPTS_SET_STD(self, args):
        # wraps __OPTS_SET
        return self.__OPTS_SET(args, "STD")

    # SET PERSISTENT (to persistent keys device store)
    def __OPTS_SET_PERS(self, args,):
        # wraps __OPTS_SET
        return self.__OPTS_SET(args, "PERS")

    # SET
    def __OPTS_SET(self, args, type):

        '''
        Set key to hold the string value. If key already holds a value,
        it is overwritten, regardless of its type. Any previous time to live
        associated with the key is discarded on successful SET operation.
            https://redis.io/commands/set

        MCU → SET#<key>#<value>@

        MCU ← 100@ (OK)
        MCU ← 202@ (KO)
        MCU ← 206@ (KO)
        MCU ← 207@ (KO)
        MCU ← 208@ (KO)
        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            value = args[1]
            rsp = False
            
            try:
                #Keys must be unique among data stores

                # STANDARD DATA STORE (even with reserved key by arancino)
                if type == 'STD':
                    
                    # check if key exist in other data store
                    if( self.datastore_rsvd.exists(key) == 1):
                        raise RedisGenericException("Duplicate Key In Persistent Data Store: ", const.ERR_REDIS_KEY_EXISTS_IN_PERS)
                    else:
                        # store the value at key
                        rsp = self.datastore.set(key, value)


                else:
                    # PERSISTENT DATA STORE
                    if type == 'PERS':
                        
                        # check if key exist in other data store
                        if( self.datastore.exists(key) == 1):
                            raise RedisGenericException("Duplicate Key In Standard Data Store: ", const.ERR_REDIS_KEY_EXISTS_IN_STD)
                        else:
                            # write to the dedicate data store (dedicated to persistent keys)
                            rsp = self.datastore_rsvd.set(key, value)

                if rsp:
                    # return ok response
                    return const.RSP_OK + const.CHR_EOT
                else:
                    # return the error code
                    return const.ERR_SET + const.CHR_EOT

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)


            # try:

            #     # STANDARD DATA STORE (even with reserved key by arancino)
            #     if type == 'STD':

            #         # if it's the reserverd key __LIBVERSION__,
            #         # then add port id to associate the device and the running version of the library
            #         if key.upper() == const.RSVD_KEY_LIBVERSION:
            #             key += self.arancino.id + const.RSVD_CHARS

            #         # check if key exist in the other data store
            #         exist = self.datastore_rsvd.exists(key)
            #         if( exist == 1):
            #             raise RedisGenericException("Duplicate Key In Persistent Data Store: ", const.ERR_REDIS_KEY_EXISTS_IN_PERS)
            #         else:
            #             rsp = self.datastore.set(key, value)

            #     # PERSISTENT DATA STORE
            #     else:
            #         if type == 'PERS':

            #             # check if key exist in the other data store
            #             exist = self.datastore.exists(key)
            #             if( exist == 1):
            #                 raise RedisGenericException("Duplicate Key In Standard Data Store: ", const.ERR_REDIS_KEY_EXISTS_IN_STD)
            #             else:
            #                 # write to the dedicate data store (dedicated to persistent keys)
            #                 rsp = self.datastore_rsvd.set(key, value)

            # except Exception as ex:
            #     raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            # if rsp:
            #     # return ok response
            #     return const.RSP_OK + const.CHR_EOT
            # else:
            #     # return the error code
            #     return const.ERR_SET + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException("Invalid arguments number for command " + const.CMD_APP_SET + ". Received: " + str(n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # GET
    def __OPTS_GET(self, args):

        '''
        Get the value of key. If the key does not exist the special value nil is returned.
        An error is returned if the value stored at key is not a string,
        because GET only handles string values.
            https://redis.io/commands/get

        MCU → GET#<key>@

        MCU ← 100#<value>@ (OK)
        MCU ← 201@ (KO)
        '''

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            rsp = None

            try:
                '''
                # It's a reserved key.
                if key.startswith(const.RSVD_CHARS) and key.endswith(const.RSVD_CHARS):

                    # if it's the reserverd key __LIBVERSION__,
                    # then add port id to associate the device and the running version of the library
                    if key.upper() == const.RSVD_KEY_LIBVERSION:
                        key += self.arancino.id + const.RSVD_CHARS

                    rsp = self.datastore_rsvd.get(key)

                # It's an application key.
                else:
                    rsp = self.datastore.get(key)
                '''
                # if it's the reserverd key __LIBVERSION__,
                # then add port id to associate the device and the running version of the library
                if key.upper() == const.RSVD_KEY_LIBVERSION:
                    key += self.arancino.id + const.RSVD_CHARS

                # first get from standard datastore
                rsp = self.datastore.get(key)

                # then try get from reserved datastore
                if rsp is None:
                    rsp = self.datastore_rsvd.get(key)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            if rsp is not None:
                # return the value
                return const.RSP_OK + const.CHR_SEP + str(rsp) + const.CHR_EOT
            else:
                # return the error code
                return const.ERR_NULL + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_GET + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # DEL
    def __OPTS_DEL(self, args):

        '''
        Removes the specified keys. A key is ignored if it does not exist.
            https://redis.io/commands/del

        MCU → DEL#<key-1>[#<key-2>#<key-n>]@

        MCU ← 100#<num-of-deleted-keys>@
        '''

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received >= n_args_required:

            try:

                #TODO delete user-reserved keys

                num = self.datastore.delete(*args)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            return const.RSP_OK + const.CHR_SEP + str(num) + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_DEL + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # KEYS
    def __OPTS_KEYS(self, args):

        '''
        Returns all keys matching pattern.
            https://redis.io/commands/keys

        MCU → KEYS[#<pattern>]@

        MCU ← 100[#<key-1>#<key-2>#<key-n>]@
        '''

        if len(args) == 0:
            pattern = '*'  # w/o pattern
        else:
            pattern = args[0]  # w/ pattern

        try:

            keys = self.datastore.keys(pattern)

        except Exception as ex:
            raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

        if len(keys) > 0:
            
            ### uncomment below to apply a filter to exclude reserved keys from returned array
            ''' 
            
            keys_filtered = []
            
            for val in keys:
                if not (val.startswith(const.RSVD_CHARS) and val.endswith(const.RSVD_CHARS)) :
                    keys_filtered.append(val)

            if len(keys) > 0:
                return const.RSP_OK + const.CHR_SEP + const.CHR_SEP.join(keys_filtered) + const.CHR_EOT
            
            else:
                return const.RSP_OK + const.CHR_EOT
            '''
            ### remove the following line when apply the patch above
            return const.RSP_OK + const.CHR_SEP + const.CHR_SEP.join(keys) + const.CHR_EOT

        else:
            return const.RSP_OK + const.CHR_EOT

    # HSET
    def __OPTS_HSET(self, args):

        '''
        Sets field in the hash stored at key to value.
        If key does not exist, a new key holding a hash is created.
        If field already exists in the hash, it is overwritten.
            https://redis.io/commands/hset

        MCU → HSET#<key>#<field>#<value>@

        MCU ← 101@
        MCU ← 102@
        '''

        n_args_required = 3
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            field = args[1]
            value = args[2]

            try:

                rsp = self.datastore.hset(key, field, value)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            if rsp == 1:
                return const.RSP_HSET_NEW + const.CHR_EOT
            else: #0
                return const.RSP_HSET_UPD + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_HSET + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # HGET
    def __OPTS_HGET(self, args):
        '''
        Returns the value associated with field in the hash stored at key.
            https://redis.io/commands/hget

        MCU → HGET#<key>#<field>@

        MCU ← 100#<value>@
        MCU ← 201@

        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            field = args[1]

            try:

                value = self.datastore.hget(key, field)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            if value is not None:
                # return the value
                return const.RSP_OK + const.CHR_SEP + str(value) + const.CHR_EOT
            else:
                # return the error code
                return const.ERR_NULL + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_HGET + ". Found: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # HGETALL
    def __OPTS_HGETALL(self, args):

        '''
        Returns all fields and values of the hash stored at key.
        In the returned value, every field name is followed by its value,
        so the length of the reply is twice the size of the hash.
            https://redis.io/commands/hgetall

        MCU → HGETALL#<key>@

        MCU ← 100[#<field-1>#<value-1>#<field-2>#<value-2>]@
        '''

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]

            rsp_str = ""

            try:

                data = self.datastore.hgetall(key) #{'field-1': 'value-1', 'field-2': 'value-2'}

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            for field in data:
                rsp_str += const.CHR_SEP + field + const.CHR_SEP + data[field]

            return const.RSP_OK + rsp_str + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_HGETALL + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # HKEYS
    def __OPTS_HKEYS(self, args):

        '''
        Returns all field names in the hash stored at key.
            https://redis.io/commands/hkeys

        MCU → HKEYS#<key>@

        MCU ← 100[#<field-1>#<field-2>]@
        '''
        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]

            try:

                fields = self.datastore.hkeys(key)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            if len(fields) > 0:
                return const.RSP_OK + const.CHR_SEP + const.CHR_SEP.join(fields) + const.CHR_EOT
            else:
                return const.RSP_OK + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_HKEYS + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # HVALS
    def __OPTS_HVALS(self, args):
        '''
        Returns all values in the hash stored at key.
            https://redis.io/commands/hvals

        MCU → HVALS#<key>

        MCU ← 100[#<value-1>#<value-2>]@
        '''
        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:
            key = args[0]

            try:

                values = self.datastore.hvals(key)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            if len(values) > 0:
                return const.RSP_OK + const.CHR_SEP + const.CHR_SEP.join(values) + const.CHR_EOT
            else:
                return const.RSP_OK + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_HVALS + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # HDEL
    def __OPTS_HDEL(self, args):
        '''
        Removes the specified fields from the hash stored at key.
        Specified fields that do not exist within this hash are ignored.
        If key does not exist, it is treated as an empty hash and this command returns 0.
            https://redis.io/commands/hdel

        MCU → HDEL#<key>#<field>[#<field-2>#<field-n>]@

        MCU ← 100#<num-of-deleted-keys>@
        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received >= n_args_required:
            idx = len(args)
            key = args[0]
            fields = args[1:idx]

            try:

                num = self.datastore.hdel(key, *fields)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            return const.RSP_OK + const.CHR_SEP + str(num) + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_HDEL + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # PUB
    def __OPTS_PUB(self, args):
        '''
        Posts a message to the given channel. Return the number of clients
        that received the message.
            https://redis.io/commands/publish

        MCU → PUB#<channel>#<message>@

        MCU ← 100#<num-of-reached-clients>@
        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received >= n_args_required:
            channel = args[0]
            message = args[1]

            try:

                num = self.datastore.publish(channel, message)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            return const.RSP_OK + const.CHR_SEP + str(num) + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_PUB + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # FLUSH
    def __OPTS_FLUSH(self, args):
        '''
        Delete all the keys of the currently application DB.
        This command never fails.
            https://redis.io/commands/flushdb

        MCU → FLUSH@

        MCU ← 100@
        '''

        n_args_required = 0
        n_args_received = len(args)

        if n_args_received >= n_args_required:

            try:

                
                #before flush, save all Reserved Keys
                rsvd_keys = self.datastore.keys(const.RSVD_CHARS + "*" + const.RSVD_CHARS)
                rsvd_keys_value = {}
                for k in rsvd_keys:
                    rsvd_keys_value[k] = self.datastore.get(k)
                
                #flush
                rsp = self.datastore.flushdb()
                
                #finally set them all again
                for k, v in rsvd_keys_value.items():
                    self.datastore.set(k, v)
                
                # flush directly the datastore; reserved keys are stored separately
                #rsp = self.datastore.flushdb()


            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            return const.RSP_OK + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_FLUSH + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)



def start():
    arancino = Arancino()
    arancino.start()

# logger
LOG = conf.logger


# list of commands
#####commands_list = const.getCommandsList()

'''
Contains all the plugged ports with a specific vid and pid. Object of type Serial.Port

Dict ports_plugged = { 
    "port id" : ArancinoPort
} 
'''


#####ports_plugged = {}



'''
Contains all the connected serial ports. Object of type Thread - SerialConnector and SerialTransport.
in 0 position there is SerialConnector instance and in position 1 there is the corresponding SerialTransport

Dict ports_connected = {
    "port id" : [SerialConnector, SerialTransport]
}
'''

#####ports_connected = {}

#####arancinoDs = ArancinoDataStore()
#####arancinoSy = ArancinoSynch()
#####arancinoDy = ArancinoPortsDiscovery()


#####arancino = Arancino()
#####arancino.start()
