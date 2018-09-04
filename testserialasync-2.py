import asyncio, serial_asyncio, serial, time, redis
from serial.tools import list_ports
from oslo_log import log as logging
from threading import Thread

LOG = logging.getLogger(__name__)

class SerialManager():
    def __init__(self):
        self.datastore = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        self.serialMonitor = SerialMonitor("Thread-SerialMonitor", self.datastore)

    def main(self):
        self.serialMonitor.start()


class SerialMonitor (Thread):

    def __init__(self, name, datastore):
        Thread.__init__(self)

        #sets the vendor and product ID to check when poll
        #TODO probably change the discovery method instead of pid e vid
        self.vid = '2a03'
        self.pid = '804F'
        self.match = self.vid + ':' + self.pid
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
            print("ports to connect to: " + port.device)
            serialConnector = SerialConnector("Thread-" + port.device, port, self.datastore)
            serialConnector.start()
            ports_connected[port.device] = serialConnector


class SerialConnector (Thread):

    def __init__(self, name, port, datastore):
        Thread.__init__(self)
        self._loop = asyncio.new_event_loop()
        self.port = port
        self.name = name
        self.baudrate = 250000
        self.datastore = datastore

    def run(self):
        self.coro = serial_asyncio.create_serial_connection(self._loop, lambda: SerialHandler(self.datastore), self.port.device, baudrate=self.baudrate)
        #self.coro = serial_asyncio.create_serial_connection(self._loop, SerialHandler, self.port.device, baudrate=self.baudrate)
        self._loop.run_until_complete(self.coro)
        self._loop.run_forever()
        self._loop.close()


class SerialHandler(asyncio.Protocol):
    def __init__(self, datastore = None):
        self.datastore = datastore

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        transport.serial.rts = False
        #transport.write( (cmd_start + ch_eot).encode() )


    def data_received(self, data):
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        print('command received: ', data.decode().strip('\n').strip('\t'))
        response = self._parseCommands(data)
        print('response sent: ',response)
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        self.transport.write(response.encode())

    def connection_lost(self, exc): #TODO gestire l'eccezione per evitare che si incricchi la seriale sulla macchina
        print('port closed ' + self.transport.serial.name)
        serial_connector = ports_connected.pop(self.transport.serial.name)
        asyncio.get_event_loop().stop()


    def _parseCommands(self, command):
        #decode the received commands
        cmd = command.decode().strip()

        #splits command by separator char
        cmd = cmd.split(CHR_SEP)

        #and then execute the command
        return self._execCommand(cmd)


    def _execCommand(self, cmd):

        idx = len(cmd)
        parameters = cmd[1:idx]

        # SET
        if cmd[0] == CMD_APP_SET:
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

        # Default
        else:
            return ERR_CMD_FOUND + CHR_SEP


    #TODO gestire in tutte le _OPTS eccezioni sul numero di argomenti, spesso capita che ne arrivano di meno:
    # IndexError: list index out of range

    # SET
    def _OPTS_SET(self, params):

        '''
        Set key to hold the string value. If key already holds a value,
        it is overwritten, regardless of its type. Any previous time to live
        associated with the key is discarded on successful SET operation.
            https://redis.io/commands/set

        MCU → SET#<key>#<value>

        MCU ← 100@ (OK)
        MCU ← 202@ (KO)
        '''

        key = params[0]
        value = params[1]

        rsp = self.datastore.set(key, value)
        if rsp:
            # return ok response
            return RSP_OK + CHR_EOT
        else:
            # return the error code
            return ERR_SET + CHR_EOT


    # GET
    def _OPTS_GET(self, args):

        '''
        Get the value of key. If the key does not exist the special value nil is returned.
        An error is returned if the value stored at key is not a string,
        because GET only handles string values.
            https://redis.io/commands/get

        MCU → GET#<key>

        MCU ← 100#<value>@ (OK)
        MCU ← 201@  (KO)
        '''

        key = args[0]

        rsp = self.datastore.get(key)

        if rsp is not None:
            # return the value
            return RSP_OK + CHR_SEP + str(rsp) + CHR_EOT
        else:
            # return the error code
            return ERR_NULL + CHR_EOT


    # DEL
    def _OPTS_DEL(self, args):

        '''
        Removes the specified keys. A key is ignored if it does not exist.
            https://redis.io/commands/del

        MCU → DEL#<key-1>[#<key-2>#<key-n>]

        MCU ← 100#<num-of-deleted-keys>@
        '''

        num = self.datastore.delete(*args)
        return RSP_OK + CHR_SEP + str(num) + CHR_EOT


    # KEYS
    def _OPTS_KEYS(self, args):

        '''
        Returns all keys matching pattern.
            https://redis.io/commands/keys

        MCU → KEYS[#<pattern>]

        MCU ← 100[#<key-1>#<key-2>#<key-n>]@
        '''

        if len(args) == 0:
            pattern = '*'  # w/o pattern
        else:
            pattern = args[0]  # w/ pattern

        keys = self.datastore.keys(pattern)

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

        MCU → HSET#<key>#<field>#<value>

        MCU ← 101@
        MCU ← 102@
        '''

        key = args[0]
        field = args[1]
        value = args[2]

        rsp = self.datastore.hset(key, field, value)

        if rsp == 1:
            return RSP_HSET_NEW + CHR_EOT
        else: #0
            return RSP_HSET_UPD + CHR_EOT


    # HGET
    def _OPTS_HGET(self, args):
        #TODO gestire eccezzione
        # redis.exceptions.ResponseError: WRONGTYPE Operation against a key holding the wrong kind of value
        # scatta quando faccio la get (semplice) di una chiave che non contiene un valore semplice ma una hashtable
        '''
        Returns the value associated with field in the hash stored at key.
            https://redis.io/commands/hget

        MCU → HGET#<key>#<field>

        MCU ← 100#<value>@
        MCU ← 201@

        '''

        key = args[0]
        field = args[1]

        value = self.datastore.hget(key, field)

        if value is not None:
            # return the value
            return RSP_OK + CHR_SEP + str(value) + CHR_EOT
        else:
            # return the error code
            return ERR_NULL + CHR_EOT


    # HGETALL
    def _OPTS_HGETALL(self, args):

        '''
        Returns all fields and values of the hash stored at key.
        In the returned value, every field name is followed by its value,
        so the length of the reply is twice the size of the hash.
            https://redis.io/commands/hgetall

        MCU → HGETALL#<key>

        MCU ← 100[#<field-1>#<value-1>#<field-2>#<value-2>]@
        '''

        key = args[0]

        rsp_str = ""

        data = self.datastore.hgetall(key) #{'field-1': 'value-1', 'field-2': 'value-2'}

        for field in data:
            rsp_str += CHR_SEP + field + CHR_SEP + data[field]

        return RSP_OK + rsp_str + CHR_EOT


    # HKEYS
    def _OPTS_HKEYS(self, args):

        '''
        Returns all field names in the hash stored at key.
            https://redis.io/commands/hkeys

        MCU → HKEYS#<key>

        MCU ← 100[#<field-1>#<field-2>]@
        '''

        key = args[0]

        fields = self.datastore.hkeys(key)

        if len(fields) > 0:
            return RSP_OK + CHR_SEP + CHR_SEP.join(fields) + CHR_EOT
        else:
            return RSP_OK + CHR_EOT


    # HVALS
    def _OPTS_HVALS(self, args):
        '''
        Returns all values in the hash stored at key.
            https://redis.io/commands/hvals

        MCU → HVALS#<key>

        MCU ← 100[#<value-1>#<value-2>]@
        '''
        key = args[0]
        values = self.datastore.hvals(key)
        if len(values) > 0:
            return RSP_OK + CHR_SEP + CHR_SEP.join(values) + CHR_EOT
        else:
            return RSP_OK + CHR_EOT


    # HDEL
    def _OPTS_HDEL(self, args):
        '''
        Removes the specified fields from the hash stored at key.
        Specified fields that do not exist within this hash are ignored.
        If key does not exist, it is treated as an empty hash and this command returns 0.
            https://redis.io/commands/hdel

        → HDEL#<key>#<field>[#<field-2>#<field-n>]

        ← 100#<num-of-deleted-keys>@
        '''

        idx = len(args)
        key = args[0]
        fields = args[1:idx]

        num = self.datastore(key, *fields)

        return RSP_OK + CHR_SEP + str(num) + CHR_EOT


#Definitions for Serial Protocol
CHR_EOT = chr(4)        #End Of Transmission Char
CHR_SEP = chr(30)       #Separator Char

CMD_SYS_START = 'START' #Start Commmand

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

RSP_OK          = '100'     #OK Response
RSP_HSET_NEW    = '101'     #Set value into a new field
RSP_HSET_UPD    = '102'     #Set value into an existing field

RSP_KO = 'KO'   #KO Response

ERR             = '200'     #Generic Error
ERR_NULL        = '201'     #Null value
ERR_SET         = '202'     #Error during SET
ERR_CMD_FOUND   = '203'     #Command Not Found

# contains all the plugged ports with a specific vid and pid. Object of type Serial.Port
ports_plugged = []

# contains all the connected serial ports. Object of type Thread - SerialConnector
ports_connected = {}

serialManager = SerialManager()
serialManager.main()
