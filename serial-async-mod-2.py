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


'''

Dict ports_plugged = { 
    "port id" : ArancinoPort
} 


Dict ports_connected = {
    "port id" : [SerialConnector, SerialTransport]
}


'''



import time,  arancino_conf as conf, signal#, uuid, hashlib, json,
import asyncio, serial_asyncio#, redis #external
#from serial.tools import list_ports
from threading import Thread
from time import localtime, strftime
import arancino_constants as const
from arancino_exceptions import InvalidArgumentsNumberException, InvalidCommandException, RedisGenericException
from arancino_port import ArancinoPortsDiscovery
from arancino_datastore import ArancinoDataStore
from arancino_synch import ArancinoSynch
import serial

#use in Lightning Rod
#from oslo_log import log as logging
#use in stand alone mode
import logging

#LOG = logging.getLogger(__name__)
##LOG = logging.getLogger("Arancino Module")
#use the following lines in standalone mode
##FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
##logging.basicConfig(level=logging.DEBUG, format=FORMAT)

LOG = conf.logger
#LOG.setLevel(logging.DEBUG) # better to have too much log than not enough
# with this pattern, it's rarely necessary to propagate the error up to parent
#LOG.propagate = False




class SerialManager():
    def __init__(self):
        try:
            self.serialMonitor = SerialMonitor("Thread-SerialMonitor")
        except Exception as ex:
            LOG.error(str(ex))
            exit(1)

    def main(self):

        self.serialMonitor.start()

        signal.signal(signal.SIGINT, self.__exit)
        signal.signal(signal.SIGTERM, self.__exit)


    def __exit(self, signum, frame):
        LOG.warning("Received Stop/Kill: Exiting... ")
        #self.kill_now = True
        self.serialMonitor.stop()


class SerialMonitor (Thread):

    def __init__(self, name):

        Thread.__init__(self)

        #self.arancinoDs = ArancinoDataStore()
        #self.arancinoSy = ArancinoSynch()

        global arancinoDs, arancinoDy

        self.datastore = arancinoDs.getDataStore()
        self.datastore.flushdb()
        self.datastore.set(const.RSVD_KEY_MODVERSION, conf.version)

        self.devicestore = arancinoDs.getDeviceStore()

        self.kill_now = False


        '''
        ##self.datastore = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        self.datastore = redis.StrictRedis(host=conf.redis['host'], port=conf.redis['port'], db=conf.redis['db'], decode_responses=conf.redis['dcd_resp'])
        self.datastore.flushdb()

        self.devicestore = redis.StrictRedis(host=conf.redis['host'], port=conf.redis['port'], db=1, decode_responses=conf.redis['dcd_resp'])

        #TODO make connection pool


        #self.match = "|".join(conf.hwid)
        #self.name = name
        #self.datastore = datastore
        self.kill_now = False
        self.datastore.set(const.RSVD_KEY_MODVERSION, "0.0.3")
        '''



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
        # TODO 2) close serial connections
        #for port in ports_connected:
        #    print(ports_connected[port])
        #    ports_connected[port].close()

        # TODO 3) set Plugged and Connecte Metadata to False in every PORT in devicestore

        LOG.info("Serial Ports Connection Closed")
        LOG.info("Exiting completed, Bye!")
        ''' EXIT PROCEDURE STOP'''

    def run(self):
        # Polls every 10 seconds if there's new serial port to connect to
        global ports_plugged, ports_connected, arancinoDs, arancinoSy

        while(True):


            if self.kill_now:
                self.__stop()
                break
            '''
            #retrieve each plugged ports which match vid and pid specified above
            #ports_plugged = list(list_ports.grep(self.match))

            #retrieve all the plugged ports
            global ports_plugged, ports_connected
            ports_plugged = list_ports.comports()
            LOG.debug("Plugged Serial Ports Retrieved: " + str(len(ports_plugged)) )

            #apply a filter
            ports_plugged = self.filterPorts(ports_plugged)
            LOG.info("Filtered Serial Ports Retrieved: " + str(len(ports_plugged)))

            #enrich list of plugged ports and transform in Dict
            ports_plugged = self.addAdditionalInfoPort(ports_plugged)
            LOG.debug(ports_plugged)
            '''

            ports_plugged = arancinoDy.getPluggedArancinoPorts(ports_plugged, ports_connected)
            LOG.info("Plugged Serial Ports Retrieved: " + str(len(ports_plugged)))
            LOG.info("Connected Serial Ports: " + str(len(ports_connected)))

            # first synchronization in cycle
            arancinoSy.synchPorts(ports_plugged)
            arancinoSy.synchClean(ports_plugged)

            #retrieve if there are new ports to connect to - is a list of type Serial.Port
            if ports_plugged:
                ports_to_connect = self.__retrieveNewPorts(ports_plugged, ports_connected)
                LOG.info("Connectable Serial Ports Retrieved: " + str(len(ports_to_connect)))

                #finally connect the new ports
                if ports_to_connect:
                    self.__connectPorts(ports_to_connect)


            self.__checkEnabledPorts(ports_plugged, ports_connected)


            # second synchronization in cycle
            arancinoSy.synchPorts(ports_plugged)

            time.sleep(conf.cycle_time)


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
        for id, arancino in plugged.items():
            if arancino.id not in connected:
                    if arancino.enabled:
                        # if true: there'are new plugged ports discovered
                        ports_to_connect.append(arancino)
                    else:
                        LOG.warning("Port Not Enabled: " + arancino.alias + " " + arancino.port.device + " - " + arancino.id)

        return ports_to_connect


    def __connectPorts(self, ports_to_connect):
        """
        For each ports in List, creates a new instance of Serial Connector and the starts it.
        Serial Connector instance is stored into a List of connected port using the
        serial number of the port as key for the List

        :param ports_to_connect: List of ListPortInfo
        :return ports_connected: List of SerialConnector
        """

        global ports_connected
        for arancino in ports_to_connect:
            LOG.info("Connecting to Port: " + arancino.alias + " " + arancino.port.device + " - " + arancino.id)

            serialConnector = SerialConnector("Thread-" + arancino.port.device, arancino.port, self.datastore, self.devicestore, baudrate = 4000000)

            arancino.connected = True
            ports_connected[arancino.id] = [serialConnector, None] # SerialConnector and SerialTransport
            serialConnector.start()


    def __checkEnabledPorts(self, plugged, connected):
        # checks if a port has been DISABLED
        # has sense only with Arancino Synch


        to_be_removed = []
        for id, p_connected in ports_connected.items():
            # ports_plugged[id]
            arancino = plugged[id]
            if arancino is not None and not arancino.enabled:
                transport = p_connected[const.IDX_SERIAL_TRANSPORT]
                transport.close()
                arancino.connected = False
                arancino.plugged = (arancino.id in arancinoDy.getPluggedArancinoPorts(plugged, connected))
                # TODO verify is this log is compliant with the others
                LOG.info("Port Closed: " + arancino.alias + " " + arancino.port.device + " - " + arancino.id)
                to_be_removed.append(id)


        for id in to_be_removed:
            connected.pop(id)


class SerialConnector (Thread):

    def __init__(self, name, port, datastore, devicestore, baudrate = 250000):
        Thread.__init__(self)
        self._loop = asyncio.new_event_loop()
        self.port = port
        self.name = name
        self.baudrate = baudrate
        self.datastore = datastore
        self.devicestore = devicestore


    def close(self):

        self._loop.stop()
        self._loop.close()
        #asyncio.get_event_loop().stop()
        #asyncio.get_event_loop().close()
        pass

    def run(self):
        #try:
            self.coro = serial_asyncio.create_serial_connection(self._loop, lambda: SerialHandler(self.datastore, self.devicestore, self.port), self.port.device, baudrate=self.baudrate)
            self._loop.run_until_complete(self.coro)
            ####### PAY ATTENTION, disabled the following line becouse i'm trying to implement the external close of the program
            self._loop.run_forever()
            self._loop.close()
        #except Exception as ex:
            #LOG.error(ex)


class SerialHandler(asyncio.Protocol):
    def __init__(self, datastore=None, devicestore=None, port=None):
        self.datastore = datastore
        self.devicestore = devicestore
        self.port = port
        self._partial = ""
        self.log_prefix = "[" + self.port.device + " - " + self.port.serial_number + "]: "

    def connection_made(self, transport):
        self.transport = transport
        #print('Port opened', transport)
        LOG.info(self.log_prefix + "Port opened: " + transport.serial.name)
        LOG.debug(self.log_prefix + "Port opened: " + str(transport))
        transport.serial.rts = False

        global ports_connected
        ports_connected[self.port.serial_number][const.IDX_SERIAL_TRANSPORT] = transport



    def connection_lost(self, exc):
        global ports_plugged, ports_connected, arancinoSy, arancinoDy

        # 1 recupare oggetto dalla plugged port in base a self.port.serialnumber
        # TODO here is used serial_number, because id is not available
        #   serial_number is part of ListPortInfo, id is part of ArancinoPort. At this moment
        #   id is derivated from serial_number and now it works, but if the way of calculate id will change
        #   this will not work anymore
        arancino = ports_plugged[self.port.serial_number]

        if arancino is not None:


        # 2 aggiornare lo stato "connected" a false
            arancino.connected = False

        # 4 capire se aggiornare acnhe plugged a false. => se il device é ancora connesso metto True (
        # lo capisco verificando la lista dei dispositivi e usando grep in base al seriale della porta.
            #arancino.plugged = (len(list(list_ports.grep(self.port.serial_number))) == 1)
            arancino.plugged = (arancino.id in arancinoDy.getPluggedArancinoPorts(ports_plugged, ports_connected))

        # 3 fare la sync. puntuale chiamando il device store ed aggiornando "connected" a false
        #TODO: non mi piace, arancino potrebbe essere None, forse é il caso di passare al
        #   SerialHandler o l'id o tutto Arancino Port cosi fixo anche il punto di sopra
        '''
        self.devicestore.hset(self.port.serial_number, "M_PLUGGED", arancino.plugged)
        self.devicestore.hset(self.port.serial_number, "M_CONNECTED", arancino.connected)
        '''
        arancinoSy.synchPort(arancino)


        # TODO verify is this log is compliant with the others
        LOG.info(self.log_prefix + "Port closed " + self.transport.serial.name)
        serial_connector = ports_connected.pop(self.port.serial_number)

        del serial_connector


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


            except InvalidArgumentsNumberException as ex:
                LOG.error(self.log_prefix + str(ex))
                response = ex.error_code + const.CHR_EOT

            except InvalidCommandException as ex:
                LOG.warning(self.log_prefix + str(ex))
                response = ex.error_code + const.CHR_EOT


            except RedisGenericException as ex:
                LOG.error(self.log_prefix + str(ex))
                response = const.ERR_REDIS + const.CHR_EOT

            except Exception as ex:
                LOG.error(self.log_prefix + str(ex))
                response = const.ERR + const.CHR_EOT

            finally:
                # send response back
                self.transport.write(response.encode())
                LOG.debug(self.log_prefix + "Sent Response: " + str(response))


            # clear the handy variable
            self._partial = ""
            #print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')

        #else:
        #    print('partial command received: ', datadec.strip('\n').strip('\t'))

    def __parseCommands(self, command):
        #decode the received commands
        #cmd = command.decode().strip()

        #splits command by separator char
        cmd = command.strip(const.CHR_EOT).split(const.CHR_SEP)

        if len(cmd) > 0:
            if cmd[0] in commands_list:
                #comando presente
                return cmd;
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
                return self.__OPTS_START()
            # SET
            elif cmd[0] == const.CMD_APP_SET:
                return self.__OPTS_SET(parameters)
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
    def __OPTS_START(self):
        '''
        Microcontroller sends START command to start communication

        MCU → START@

        MCU  ← 100@ (OK)
        '''
        return const.RSP_OK + const.CHR_EOT

    # SET
    def __OPTS_SET(self, args):

        '''
        Set key to hold the string value. If key already holds a value,
        it is overwritten, regardless of its type. Any previous time to live
        associated with the key is discarded on successful SET operation.
            https://redis.io/commands/set

        MCU → SET#<key>#<value>@

        MCU ← 100@ (OK)
        MCU ← 202@ (KO)
        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            value = args[1]

            try:

                rsp = self.datastore.set(key, value)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            if rsp:
                # return ok response
                return const.RSP_OK + const.CHR_EOT
            else:
                # return the error code
                return const.ERR_SET + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_SET + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)

    # GET
    def __OPTS_GET(self, args):

        '''
        Get the value of key. If the key does not exist the special value nil is returned.
        An error is returned if the value stored at key is not a string,
        because GET only handles string values.
            https://redis.io/commands/get

        MCU → GET#<key>@

        MCU ← 100#<value>@ (OK)
        MCU ← 201@  (KO)
        '''

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]

            try:

                rsp = self.datastore.get(key)

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

        MCU → PUSH#<channel>#<message>@

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
        Delete all the keys of the currently selected DB. 
        This command never fails.
            https://redis.io/commands/flushdb

        MCU → FLUSH@

        MCU ← 100@
        '''

        n_args_required = 0
        n_args_received = len(args)

        if n_args_received >= n_args_required:
            idx = len(args)
            channel = args[0]
            message = args[1]

            try:

                rsp = self.datastore.flushdb()

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            return const.RSP_OK + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + const.CMD_APP_FLUSH + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", const.ERR_CMD_PRM_NUM)


# list of commands
commands_list = const.getCommandsList()

# contains all the plugged ports with a specific vid and pid. Object of type Serial.Port
#global ports_plugged
ports_plugged = {}


# contains all the connected serial ports. Object of type Thread - SerialConnector
#global ports_connected
ports_connected = {}

arancinoDs = ArancinoDataStore()
arancinoSy = ArancinoSynch()
arancinoDy = ArancinoPortsDiscovery()


serialManager = SerialManager()
serialManager.main()


#TODO quando c'é una scheda connessa sul device store PLUGGED = TRUE
# appena la stacco, PLUGGED rimane  TRUE perche essendo la sync
# impostata sul Dict delle plugged_ports allora non aggiorna piu quella scheda
# Nella sync andrebbero spazzolate tutte le schede ed impostare
# CONNECTED=FALSE e PLUGGED = FALSE