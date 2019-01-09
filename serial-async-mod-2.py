import time,  conf, uuid, hashlib, json, signal
import asyncio, serial_asyncio, redis #external
from serial.tools import list_ports
from threading import Thread

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


class InvalidArgumentsNumberException(Exception):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(InvalidArgumentsNumberException, self).__init__(message)

        # Now for your custom code...
        self.error_code = error_code


class InvalidCommandException(Exception):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(InvalidCommandException, self).__init__(message)

        # Now for your custom code...
        self.error_code = error_code


class RedisGenericException(Exception):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(RedisGenericException, self).__init__(message)

        # Now for your custom code...
        self.error_code = error_code



class SerialManager():
    def __init__(self):

        self.serialMonitor = SerialMonitor("Thread-SerialMonitor")


    def main(self):

        self.serialMonitor.start()

        signal.signal(signal.SIGINT, self.__exit)
        signal.signal(signal.SIGTERM, self.__exit)


    def __exit(self, signum, frame):
        LOG.warning("Received Stop/Kill: Exiting... ")
        #self.kill_now = True
        self.serialMonitor.stop()


class SerialMonitor (Thread):

    ### keys used in the list of the ports

    # additional metadata keys
    __M_ID = "M_ID"
    __M_ENABLED = "M_ENABLED"
    __M_AUTO_RECONNECT = "M_AUTORECONNECT"
    __M_CONNECTED = "M_CONNECTED"
    __M_PLUGGED = "M_PLUGGED"
    __M_ALIAS = "M_ALIAS"

    # ports info keys
    __P_DEVICE = "P_DEVICE"
    __P_NAME = "P_NAME"
    __P_DESCRIPTION = "P_DESCRIPTION"
    __P_HWID = "P_HWID"
    __P_VID = "P_VID"
    __P_PID = "P_PID"
    __P_SERIALNUMBER = "P_SERIALNUMBER"
    __P_LOCATION = "P_LOCATION"
    __P_MANUFACTURER = "P_MANUFACTURER"
    __P_PRODUCT = "P_PRODUCT"
    __P_INTERFACE = "P_INTERFACE"

    # object keys
    __O_PORT = "O_PORT" #ListPortInfo
    __O_SERIAL = "O_SERIAL" #SerialConnector


    def __init__(self, name):
        Thread.__init__(self)




        #sets the vendor and product ID to check when poll
        #TODO probably change the discovery method instead of pid e vid
        #self.vid = '2a03'
        #self.pid = '804F'
        #self.match = self.vid + ':' + self.pid

        ##self.datastore = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        self.datastore = redis.StrictRedis(host=conf.redis['host'], port=conf.redis['port'], db=conf.redis['db'], decode_responses=conf.redis['dcd_resp'])
        self.datastore.flushdb()

        self.devicestore = redis.StrictRedis(host=conf.redis['host'], port=conf.redis['port'], db=1, decode_responses=conf.redis['dcd_resp'])

        #TODO make connection pool


        #self.match = "|".join(conf.hwid)
        #self.name = name
        #self.datastore = datastore
        self.kill_now = False
        self.datastore.set(RSVD_KEY_MODVERSION, "0.0.3")

    # public function
    def stop(self):
        self.kill_now = True

    # private function, makes the real stop. invoked by the thread.
    def __stop(self):
        ''' EXIT PROCEDURE START'''
        LOG.debug("Closing Redis Connection...")
        self.datastore.connection_pool.disconnect()
        LOG.info("Redis Connection Closed")
        LOG.debug("Closing Serial Ports Connection...")
        # TODO 2) close serial connections
        for port in ports_connected:
            print(ports_connected[port])
            ports_connected[port].close()

        LOG.info("Serial Ports Connection Closed")
        LOG.info("Exiting completed, Bye!")
        ''' EXIT PROCEDURE STOP'''

    def run(self):
        # Polls every 10 seconds if there's new serial port to connect to
        while(True):


            if self.kill_now:
                self.__stop()
                break

            #retrieve each plugged ports which match vid and pid specified above
            #ports_plugged = list(list_ports.grep(self.match))

            #retrieve all the plugged ports
            global ports_plugged, ports_connected
            ports_plugged = list_ports.comports()
            LOG.debug("Plugged Serial Ports Retrieved: " + str(len(ports_plugged)) )

            #apply a filter
            ports_plugged = self.filterPorts(ports_plugged)
            LOG.info("Filtered Serial Ports Retrieved: " + str(len(ports_plugged)))

            #enrich and transform the list of plugged ports
            ports_plugged = self.addAdditionalInfoPort(ports_plugged)
            LOG.debug(ports_plugged)




            #TODO make a synch with the devicestore


'''
            #retrieve if there are new ports to connect - is a list of type Serial.Port
            if ports_plugged:
                ports_to_connect = self.retrieveNewPorts(ports_plugged, ports_connected)

                #finally connect the new ports
                if ports_to_connect:
                    self.connectPorts(ports_to_connect)
'''
            #TODO eseguire la stessa funzione di sopra di synch con il devicestore
            time.sleep(10000)


    def retrieveNewPorts(self, plugged, connected):
        #print('checking differences')
        ports_to_connect = []
        for pp in plugged:
            port = plugged[pp]
            #TODO introduce new checks eg: verify "enabled" field or "autoreconnect"
            if port[self.__O_PORT].serial_number not in connected and port[self.__M_ENABLED]:
                # if true: there'are new plugged ports discovered
                ports_to_connect.append(port)
        return ports_to_connect


    def connectPorts(self, ports_to_connect):
        '''
        Connect to each Serial Port in list
        :param ports_to_connect: List of ListPortInfo
        :return ports_connected: List of SerialConnector
        '''

        global ports_connected
        for port in ports_to_connect:
            LOG.info("Ports to connect to: " + port[self.__O_PORT].device)

            serialConnector = SerialConnector("Thread-" + port[self.__O_PORT].device, port[self.__O_PORT], self.datastore, self.devicestore, baudrate = 4000000)

            port[self.__M_CONNECTED] = True
            #ports_connected[port["port"].device] = serialConnector
            ports_connected[port[self.__O_PORT].serial_number] = serialConnector
            serialConnector.start()


    def addAdditionalInfoPort(self, ports):
        '''
        Create a new struture starting from a List of ListPortInfo this methods.
        A base element of the new structure is composed by some metadata and
            the starting object of type ListPortInfo


        :param ports: List of plugged port (ListPortInfo)
        :return: Dict of Ports with additional information
        '''

        new_ports_struct = {}

        for port in ports:
            p ={}
            p[self.__M_ID] = str(port.serial_number)
            p[self.__M_ENABLED] = True
            p[self.__M_AUTO_RECONNECT] = False
            p[self.__M_CONNECTED] = False
            p[self.__M_PLUGGED] = True
            p[self.__M_ALIAS] = ""

            p[self.__O_PORT] = port

            new_ports_struct[p[self.__M_ID]] = p

        return new_ports_struct

    def filterPorts(self, ports):
        '''
        Filters Serial Ports with Serial Number, VID and PID
        :param ports: List of ListPortInfo
        :return ports_filterd: List
        '''
        ports_filterd = []

        for port in ports:
            #filters serial with
            #TODO enable the filter
            if port.serial_number != None and port.serial_number != "FFFFFFFFFFFFFFFFFFFF" and port.vid != None and port.pid != None:

                #ports_filterd.append(port)
                #ports_filterd_serialized.append(self.serializePort(port))

                # create a new object containing the port (ListPortInfo) and additional serialized informations
                #p = self.additionalInfoPort(port, plugged=True)
                #p[self.__O_PORT] = port
                #ports_filterd[p[self.__M_ID]] = p

                ports_filterd.append(port)


        return ports_filterd


    def syncPorts(self, ports):
        '''
        Makes a synchroinization bewteen the list of plugged ports and the device store (redis db 1)
        :param ports:
        :return:
        '''
        # 1. load from device store
        # 2. make diff
        # 2.1 partendo da quelli presenti su ports_plugged verificare se esiste la controparte sul deveice store
        # 2.2 se esiste aggiornare i metadati su ports_plugged: DB to LIST
        #    enabled, autoreconnect, alias
        # 2.3 se esiste aggiornare i metadadi sul devicestore: LIST to DB
        #   plugged, connected, ed altri relativi alla porta (ad esempio il device :/dev/tty.ACM0, location ed altri.
        # 3 se non esiste, inserirla

        for port in ports:

            # get from device store
            if self.devicestore.exists(port[self.__M_ID]) == 1: # the port is already registered in the device store

                # TODO: pay attention with boolean data and None value

                # update metadata in the list (from redis to list in memory)
                port[self.__M_ENABLED] = self.devicestore.hget(port[self.__M_ID], self.__M_ENABLED)
                port[self.__M_AUTO_RECONNECT] = self.devicestore.hget(port[self.__M_ID], self.__M_AUTO_RECONNECT)
                port[self.__M_ALIAS] = self.devicestore.hget(port[self.__M_ID], self.__M_ALIAS)

                # update metadata in the list (from list to redis)
                self.devicestore.hset(port[self.__M_ID], self.__M_PLUGGED, port[self.__M_PLUGGED])
                self.devicestore.hset(port[self.__M_ID], self.__M_CONNECTED, port[self.__M_CONNECTED])
                #self.devicestore.hset(port[self.__M_ID], self.__P_DEVICE, port[self.__P_DEVICE])
                #self.devicestore.hset(port[self.__M_ID], self.__P_LOCATION, port[self.__P_LOCATION])
                #self.devicestore.hset(port[self.__M_ID], self.__P_INTERFACE, port[self.__P_INTERFACE])

            else: #the port does not exist in the device store and must be registered

                # TODO: pay attention with boolean data and None value
                # use the value of the port id as key in hash of redis, the defined above keys as fields, and values as values
                self.devicestore.hset(port[self.__M_ID], self.__M_ENABLED , port[self.__M_ENABLED])
                self.devicestore.hset(port[self.__M_ID], self.__M_AUTO_RECONNECT, port[self.__M_AUTO_RECONNECT])
                self.devicestore.hset(port[self.__M_ID], self.__M_CONNECTED, port[self.__M_CONNECTED])
                self.devicestore.hset(port[self.__M_ID], self.__M_PLUGGED, port[self.__M_PLUGGED])
                self.devicestore.hset(port[self.__M_ID], self.__M_ALIAS, port[self.__M_ALIAS])
                self.devicestore.hset(port[self.__M_ID], self.__P_NAME, port[self.__O_PORT].name)
                self.devicestore.hset(port[self.__M_ID], self.__P_DESCRIPTION, port[self.__O_PORT].description)
                self.devicestore.hset(port[self.__M_ID], self.__P_HWID, port[self.__O_PORT].hwid)
                self.devicestore.hset(port[self.__M_ID], self.__P_VID, hex(port[self.__O_PORT].vid))
                self.devicestore.hset(port[self.__M_ID], self.__P_PID, hex(port[self.__O_PORT].pid))
                self.devicestore.hset(port[self.__M_ID], self.__P_SERIALNUMBER, port[self.__O_PORT].serial_number)
                self.devicestore.hset(port[self.__M_ID], self.__P_MANUFACTURER, port[self.__O_PORT].manufacturer)
                self.devicestore.hset(port[self.__M_ID], self.__P_PRODUCT, port[self.__O_PORT].product)

            self.devicestore.hset(port[self.__M_ID], self.__P_DEVICE, port[self.__O_PORT].device)
            self.devicestore.hset(port[self.__M_ID], self.__P_LOCATION, port[self.__O_PORT].location)
            self.devicestore.hset(port[self.__M_ID], self.__P_INTERFACE, port[self.__O_PORT].interface)


    def __encrypt_string(self, hash_string):
        sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
        return sha_signature

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
    def __init__(self, datastore = None, devicestore = None, port = None):
        self.datastore = datastore
        self.devicestore = devicestore
        self.port = port
        self._partial = ""

    def connection_made(self, transport):
        self.transport = transport
        #print('Port opened', transport)
        LOG.info("Port opened: " + transport.serial.name)
        LOG.debug("Port opened: " + str(transport))
        transport.serial.rts = False

    def connection_lost(self, exc):
        global ports_plugged
        print("AAAAAAAAAAA")
        print(ports_plugged)
        print("AAAAAAAAAAA")

        # 1 recupare oggetto dalla plugged port in base a self.port.serialnumber

        # 2 aggiornare lo stato "connected" a false

        # 3 fare la sync. puntuale chiamando il device store ed aggiornando "connected" a false

        # 4 capire se aggiornare acnhe plugged a false.

        LOG.info('Port closed ' + self.transport.serial.name)
        serial_connector = ports_connected.pop(self.transport.serial.name)

        ####TODO Test DEL
        del serial_connector
        asyncio.get_event_loop().stop()

    def data_received(self, data):

        #print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        datadec = data.decode()
        self._partial += datadec

        if self._partial.endswith(CHR_EOT) is True:
            # now command is completed and can be used
            LOG.debug('Received Command: ' + self._partial.strip('\n').strip('\t'))
            #print('Received Command: ', self._partial.strip('\n').strip('\t'))

            try:
                # parse and check command
                cmd = self._parseCommands(self._partial)

                # then execute it
                response = self._execCommand(cmd)


            except InvalidArgumentsNumberException as ex:
                LOG.error(str(ex))
                response = ex.error_code + CHR_EOT

            except InvalidCommandException as ex:
                LOG.warn(str(ex))
                response = ex.error_code + CHR_EOT


            except RedisGenericException as ex:
                LOG.error(str(ex))
                response = ERR_REDIS + CHR_EOT

            except Exception as ex:
                LOG.error(str(ex))
                response = ERR + CHR_EOT

            finally:
                # send response back
                self.transport.write(response.encode())
                #print('Sent Response: ', response)
                LOG.debug('Sent Response: ' + str(response))


            # clear the handy variable
            self._partial = ""
            #print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')

        #else:
        #    print('partial command received: ', datadec.strip('\n').strip('\t'))

    def _parseCommands(self, command):
        #decode the received commands
        #cmd = command.decode().strip()

        #splits command by separator char
        cmd = command.strip(CHR_EOT).split(CHR_SEP)

        if len(cmd) > 0:
            if cmd[0] in commands_list:
                #comando presente
                return cmd;
            else:
                raise InvalidCommandException("Command does not exist: " + cmd[0] + " - Skipped", ERR_CMD_NOT_FND)
        else:
            raise InvalidCommandException("No command received", ERR_CMD_NOT_RCV)

        return cmd;

    def _execCommand(self, cmd):

        idx = len(cmd)
        parameters = cmd[1:idx]
        '''
        _OPTIONS = {
            CMD_SYS_START: self._OPTS_START,
            CMD_APP_SET: self._OPTS_SET,
            CMD_APP_GET: self._OPTS_GET,
            CMD_APP_DEL: self._OPTS_DEL,
            CMD_APP_KEYS: self._OPTS_KEYS,
            CMD_APP_HSET: self._OPTS_HSET,
            CMD_APP_HGETALL: self._OPTS_HGETALL,
            CMD_APP_HKEYS: self._OPTS_HKEYS,
            CMD_APP_HVALS: self._OPTS_HVALS,
            CMD_APP_HDEL: self._OPTS_HDEL
        }

        _opts = _OPTIONS.get(cmd[0], lambda : ERR_CMD_NOT_FND + CHR_SEP)
        return _opts(parameters)
        '''
        try:
            # START
            if cmd[0] == CMD_SYS_START:
                return self._OPTS_START()
            # SET
            elif cmd[0] == CMD_APP_SET:
                return self._OPTS_SET(parameters)
            # GET
            elif cmd[0] == CMD_APP_GET:
                return self._OPTS_GET(parameters)
            # DEL
            elif cmd[0] == CMD_APP_DEL:
                return self._OPTS_DEL(parameters)
            # KEYS
            elif cmd[0] == CMD_APP_KEYS:
                return self._OPTS_KEYS(parameters)
            # HSET
            elif cmd[0] == CMD_APP_HSET:
                return self._OPTS_HSET(parameters)
            # HGET
            elif cmd[0] == CMD_APP_HGET:
                return self._OPTS_HGET(parameters)
            # HGETALL
            elif cmd[0] == CMD_APP_HGETALL:
                return self._OPTS_HGETALL(parameters)
            # HKEYS
            elif cmd[0] == CMD_APP_HKEYS:
                return self._OPTS_HKEYS(parameters)
            # HVALS
            elif cmd[0] == CMD_APP_HVALS:
                return self._OPTS_HVALS(parameters)
            # HDEL
            elif cmd[0] == CMD_APP_HDEL:
                return self._OPTS_HDEL(parameters)
            # PUB
            elif cmd[0] == CMD_APP_PUB:
                return self._OPTS_PUB(parameters)
            # FLUSH
            elif cmd[0] == CMD_APP_FLUSH:
                return self._OPTS_FLUSH(parameters)
            # Default
            else:
                return ERR_CMD_NOT_FND + CHR_SEP

        except Exception as ex:
            # generic error handler which raise back exception
            raise ex

    # START
    def _OPTS_START(self):
        '''
        Microcontroller sends START command to start communication

        MCU → START@

        MCU  ← 100@ (OK)
        '''
        return RSP_OK + CHR_EOT

    # SET
    def _OPTS_SET(self, args):

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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            if rsp:
                # return ok response
                return RSP_OK + CHR_EOT
            else:
                # return the error code
                return ERR_SET + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_SET + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # GET
    def _OPTS_GET(self, args):

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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            if rsp is not None:
                # return the value
                return RSP_OK + CHR_SEP + str(rsp) + CHR_EOT
            else:
                # return the error code
                return ERR_NULL + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_GET + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # DEL
    def _OPTS_DEL(self, args):

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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            return RSP_OK + CHR_SEP + str(num) + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_DEL + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # KEYS
    def _OPTS_KEYS(self, args):

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
            raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

        if len(keys) > 0:
            return RSP_OK + CHR_SEP + CHR_SEP.join(keys) + CHR_EOT
        else:
            return RSP_OK + CHR_EOT

    # HSET
    def _OPTS_HSET(self, args):

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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            if rsp == 1:
                return RSP_HSET_NEW + CHR_EOT
            else: #0
                return RSP_HSET_UPD + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_HSET + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # HGET
    def _OPTS_HGET(self, args):
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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            if value is not None:
                # return the value
                return RSP_OK + CHR_SEP + str(value) + CHR_EOT
            else:
                # return the error code
                return ERR_NULL + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_HGET + ". Found: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # HGETALL
    def _OPTS_HGETALL(self, args):

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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            for field in data:
                rsp_str += CHR_SEP + field + CHR_SEP + data[field]

            return RSP_OK + rsp_str + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_HGETALL + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # HKEYS
    def _OPTS_HKEYS(self, args):

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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            if len(fields) > 0:
                return RSP_OK + CHR_SEP + CHR_SEP.join(fields) + CHR_EOT
            else:
                return RSP_OK + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_HKEYS + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # HVALS
    def _OPTS_HVALS(self, args):
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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            if len(values) > 0:
                return RSP_OK + CHR_SEP + CHR_SEP.join(values) + CHR_EOT
            else:
                return RSP_OK + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_HVALS + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # HDEL
    def _OPTS_HDEL(self, args):
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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            return RSP_OK + CHR_SEP + str(num) + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_HDEL + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # PUB
    def _OPTS_PUB(self, args):
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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            return RSP_OK + CHR_SEP + str(num) + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_PUB + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)

    # FLUSH
    def _OPTS_FLUSH(self, args):
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
                raise RedisGenericException("Redis Error: " + str(ex), ERR_REDIS)

            return RSP_OK + CHR_SEP + str(num) + CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + CMD_APP_FLUSH + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", ERR_CMD_PRM_NUM)


#Definitions for Serial Protocol
CHR_EOT = chr(4)            #End Of Transmission Char
CHR_SEP = chr(30)           #Separator Char

CMD_SYS_START   = 'START' #Start Commmand

CMD_APP_GET     = 'GET'     #Get value at key
CMD_APP_SET     = 'SET'     #Set value at key
CMD_APP_DEL     = 'DEL'     #Delete one or multiple keys
CMD_APP_KEYS    = 'KEYS'    #Get keys by a pattern
CMD_APP_HGET    = 'HGET'    #
CMD_APP_HGETALL = 'HGETALL' #
CMD_APP_HKEYS   = 'HKEYS'   #
CMD_APP_HVALS   = 'HVALS'   #
CMD_APP_HDEL    = 'HDEL'    #
CMD_APP_HSET    = 'HSET'    #
CMD_APP_PUB     = 'PUB'     #
CMD_APP_FLUSH   = 'FLUSH'   #Flush the current Database, delete all the keys from the current Database

RSP_OK          = '100'     #OK Response
RSP_HSET_NEW    = '101'     #Set value into a new field
RSP_HSET_UPD    = '102'     #Set value into an existing field

ERR             = '200'     #Generic Error
ERR_NULL        = '201'     #Null value
ERR_SET         = '202'     #Error during SET
ERR_CMD_NOT_FND = '203'     #Command Not Found
ERR_CMD_NOT_RCV = '204'     #Command Not Received
ERR_CMD_PRM_NUM = '205'     #Invalid parameter number
ERR_REDIS       = '206'     #Generic Redis Error

#Reserved keys
RSVD_KEY_MONITOR = "___MONITOR___"
RSVD_KEY_LIBVERSION = "___LIBVERS___"
RSVD_KEY_MODVERSION = "___MODVERS___"


# list of commands
commands_list = [CMD_SYS_START, CMD_APP_GET, CMD_APP_SET, CMD_APP_DEL, CMD_APP_KEYS, CMD_APP_HGET, CMD_APP_HGETALL, CMD_APP_HKEYS, CMD_APP_HVALS, CMD_APP_HDEL, CMD_APP_HSET, CMD_APP_PUB, CMD_APP_FLUSH]

# contains all the plugged ports with a specific vid and pid. Object of type Serial.Port
#global ports_plugged
ports_plugged = {}



# contains all the connected serial ports. Object of type Thread - SerialConnector
#global ports_connected
ports_connected = {}

serialManager = SerialManager()
serialManager.main()
