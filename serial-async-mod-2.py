import asyncio, serial_asyncio, serial, time, redis, conf
from serial.tools import list_ports
from threading import Thread

#use in Lightning Rod
#from oslo_log import log as logging
#use in stand alone mode
import logging

#LOG = logging.getLogger(__name__)
LOG = logging.getLogger("Arancino Module")
#use the following lines in standalone mode
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


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

        #self.datastore = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        self.datastore = redis.StrictRedis(host=conf.redis['host'], port=conf.redis['port'], db=conf.redis['db'], decode_responses=conf.redis['dcd_resp'])
        self.datastore.flushdb()
        self.serialMonitor = SerialMonitor("Thread-SerialMonitor", self.datastore)

    def main(self):
        self.serialMonitor.start()


class SerialMonitor (Thread):

    def __init__(self, name, datastore):
        Thread.__init__(self)

        #sets the vendor and product ID to check when poll
        #TODO probably change the discovery method instead of pid e vid
        #self.vid = '2a03'
        #self.pid = '804F'
        #self.match = self.vid + ':' + self.pid

        self.match = "|".join(conf.hwid)
        self.name = name
        self.datastore = datastore

    def run(self):
        # Polls every 10 seconds if there's new serial port to connect to
        while(True):

            #retrieve each plugged ports which match vid and pid specified above
            ports_plugged = list(list_ports.grep(self.match))

            #retrieve if there are new ports to connect - is a list of type Serial.Port
            if ports_plugged:
                ports_to_connect = self.retrieveNewPorts(ports_plugged, ports_connected)

                #finally connect the new ports
                if ports_to_connect:
                    self.connectPorts(ports_to_connect)

            time.sleep(10)

    def retrieveNewPorts(self, plugged, connected):
        #print('checking differences')
        ports_to_connect = []
        for port in plugged:
            if port.device not in connected:
                ports_to_connect.append(port)
        return ports_to_connect

    def connectPorts(self, ports_to_connect):
        for port in ports_to_connect:
            LOG.info("Ports to connect to: " + port.device)
            #print("ports to connect to: " + port.device)
            serialConnector = SerialConnector("Thread-" + port.device, port, self.datastore, baudrate = 4000000)
            serialConnector.start()
            ports_connected[port.device] = serialConnector


class SerialConnector (Thread):

    def __init__(self, name, port, datastore, baudrate = 250000):
        Thread.__init__(self)
        self._loop = asyncio.new_event_loop()
        self.port = port
        self.name = name
        self.baudrate = baudrate
        self.datastore = datastore

    def run(self):
        #try:
            self.coro = serial_asyncio.create_serial_connection(self._loop, lambda: SerialHandler(self.datastore), self.port.device, baudrate=self.baudrate)
            self._loop.run_until_complete(self.coro)
            self._loop.run_forever()
            self._loop.close()
        #except Exception as ex:
            #LOG.error(ex)


class SerialHandler(asyncio.Protocol):
    def __init__(self, datastore = None):
        self.datastore = datastore
        self._partial = ""

    def connection_made(self, transport):
        self.transport = transport
        #print('Port opened', transport)
        LOG.info("Port opened: " + transport.serial.name)
        LOG.debug("Port opened: " + str(transport))
        transport.serial.rts = False

    def connection_lost(self, exc):
        LOG.info('Port closed ' + self.transport.serial.name)
        serial_connector = ports_connected.pop(self.transport.serial.name)
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
RSVD_KEY_MONITOR = "___VERSION___"


# list of commands
commands_list = [CMD_SYS_START, CMD_APP_GET, CMD_APP_SET, CMD_APP_DEL, CMD_APP_KEYS, CMD_APP_HGET, CMD_APP_HGETALL, CMD_APP_HKEYS, CMD_APP_HVALS, CMD_APP_HDEL, CMD_APP_HSET, CMD_APP_PUB, CMD_APP_FLUSH]

# contains all the plugged ports with a specific vid and pid. Object of type Serial.Port
ports_plugged = []

# contains all the connected serial ports. Object of type Thread - SerialConnector
ports_connected = {}

serialManager = SerialManager()
serialManager.main()
