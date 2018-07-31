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
        print('checking differences')
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
        print('data received ', data.decode())
        response = self._parseCommands(data)
        print(response)
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

        #SET
        if cmd[0] == CMD_APP_SET:
            return self._OPTS_SET(parameters)
        #GET
        elif cmd[0] == CMD_APP_GET:
            return self._OPTS_GET(parameters)
        #DEL
        elif cmd[0] == CMD_APP_DEL:
            return self._OPTS_DEL(parameters)
        #KEYS
        elif cmd[0] == CMD_APP_KEYS:
            return self._OPTS_KEYS(parameters)

    # SET
    def _OPTS_SET(self, params):

        '''
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
        https://redis.io/commands/del

        MCU → DEL#<key-1>[#<key-2>#<key-n>]

        MCU ← 100#<num-of-deleted-keys>@
        '''

        num = self.datastore.delete(*args)
        return RSP_OK + CHR_SEP + str(num) + CHR_EOT


    # KEYS
    def _OPTS_KEYS(self, args):

        '''
        https://redis.io/commands/keys

        MCU → KEYS[#<pattern>]

        MCU ← 100[#<key-1>#<key-2>#<key-n>]@
        '''

        if len(args) == 1:
            pattern = args[0] # w/ pattern
        else:
            pattern = '*'  # w/o pattern

        keys = self.datastore.keys(pattern)

        if len(keys) > 0:
            return RSP_OK + CHR_SEP + CHR_SEP.join(keys) + CHR_EOT
        else:
            return RSP_OK + CHR_EOT


    # HSET
    def _OPTS_HSET(self, args):

        '''
        MCU → HSET#<key>#<field>#<value>

        MCU ← 101@
        MCU ← 102@
        '''

        key = args[0]
        field = args[1]
        value = args[2]

        rsp = self.datastore.hset(key, field, value)

        if rsp == 0:
            return RSP_HSET_NEW + CHR_EOT
        else: #1
            return RSP_HSET_UPD + CHR_EOT


    # HGET
    def _OPTS_HGET(self, args):
        #TODO gestire eccezzione
        # redis.exceptions.ResponseError: WRONGTYPE Operation against a key holding the wrong kind of value
        # scatta quando faccio la get (semplice) di una chiave che non contiene un valore semplice ma una hashtable
        '''

        MCU → HGET#<key>#<field>

        MCU ← 100#<value>@
        MCU ← 201@

        '''

        key = args[1]
        field = args[2]

        value = self.datastore.get(key, field)

        if value is not None:
            # return the value
            return RSP_OK + CHR_SEP + str(value) + CHR_EOT
        else:
            # return the error code
            return ERR_NULL + CHR_EOT


    # HGETALL
    def _OPTS_HGET_ALL(self, args):

        '''
        MCU → HGETALL#<key>

        MCU ← 100[#<field-1>#<value-1>#<field-2>#<value-2>]@
        '''

        key = args[1]

        rsp_str = ""

        data = self.datastore.hgetall(key) #{'field-1': 'value-1', 'field-2': 'value-2'}

        for field in data:
            rsp_str += CHR_SEP + field + CHR_SEP + data[field]

        return RSP_OK + rsp_str + CHR_EOT


    # HKEYS
    def _OPTS_HKEYS(self, args):

        '''
        MCU → HKEYS#<key>

        MCU ← 100[#<field-1>#<field-2>]@
        '''

        key = args[0]

        fields = self.datastore.keys(key)

        if len(fields) > 0:
            return RSP_OK + CHR_SEP + CHR_SEP.join(fields) + CHR_EOT
        else:
            return RSP_OK + CHR_EOT

    # HVALS
    def _OPTS_HVALS(self, args):
        '''
        HVALS:

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
        HDEL:

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
CMD_APP_VALS    = 'HVALS'   #
CMD_APP_HDEL    = 'HDEL'    #
CMD_APP_HSET    = 'HSET'    #

RSP_OK          = '100'     #OK Response
RSP_HSET_NEW    = '101'     #Set value into a new field
RSP_HSET_UPD    = '102'     #Set value into an existing field

RSP_KO = 'KO'   #KO Response

ERR             = '200'     #Generic Error
ERR_NULL        = '201'     #Null value
ERR_SET         = '202'     #Error during SET
#ERR_NOT_FOUND   = '203'     #Not Found

# contains all the plugged ports with a specific vid and pid. Object of type Serial.Port
ports_plugged = []

# contains all the connected serial ports. Object of type Thread - SerialConnector
ports_connected = {}

serialManager = SerialManager()
serialManager.main()
