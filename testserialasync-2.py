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

        #SET
        if cmd[0] == CMD_APP_SET:
            return self._OPTS_SET(cmd)
        #GET
        elif cmd[0] == CMD_APP_GET:
            return self._OPTS_GET(cmd)
        #DEL
        elif cmd[0] == CMD_APP_DEL:
            return self._OPTS_DEL(cmd)
        #KEYS
        elif cmd[0] == CMD_APP_KEYS:
            self._OPTS_KEYS(cmd)

    # SET
    def _OPTS_SET(self, cmd):

        '''
        MCU → SET#<key>#<value>

        MCU ← 100@ (OK)
        MCU ← 202@ (KO)
        '''

        key = cmd[1]
        value = cmd[2]

        rsp = self.datastore.set(key, value)
        if rsp:
            # return ok response
            return RSP_OK + CHR_EOT
        else:
            # return the error code
            return ERR_SET + CHR_EOT


    # GET
    def _OPTS_GET(self, cmd):

        '''
        MCU → GET#<key>

        MCU ← 100#<value>@ (OK)
        MCU ← 201@  (KO)
        '''

        key = cmd[1]

        rsp = self.datastore.get(key)

        if rsp is not None:
            # return the value
            return RSP_OK + CHR_SEP + str(rsp) + CHR_EOT
        else:
            # return the error code
            return ERR_NULL + CHR_EOT


    # DEL
    def _OPTS_DEL(self, cmd):

        '''
        DEL:

        MCU → DEL#<key-1>[#<key-2>#<key-n>]

        MCU ← 100#<num-of-deleted-keys>@
        '''

        idx = len(cmd)
        keys = cmd[1:idx]

        rsp = self.datastore.delete(*keys)
        return RSP_OK + CHR_SEP + str(rsp) + CHR_EOT


    # KEYS
    def _OPTS_KEYS(self, cmd):

        '''
        MCU → KEYS[#<pattern>]

        MCU ← 100[#<key-1>#<key-2>#<key-n>]@
        '''

        if len(cmd) == 2:
            pattern = cmd[1] # w/ pattern
        else:
            pattern = '*'  # w/o pattern

        rsp = self.datastore.keys(pattern)

        rsp_str = RSP_OK

        for key in rsp:
            #TODO CHR_SEP deve essere inserito alla fine, e non se la chiave é l'ultima
            rsp_str += CHR_SEP + key

        return rsp_str + CHR_EOT

    # HSET
    def _OPTS_HSET(self, cmd):

        '''
        MCU → HSET#<key>#<field>#<value>

        MCU ← 101@
        MCU ← 102@
        '''

        key = cmd[1]
        field = cmd[2]
        value = cmd[3]

        rsp = self.datastore.hset(key, field, value)

        if rsp == 0:
            return RSP_HSET_NEW + CHR_EOT
        else: #1
            return RSP_HSET_UPD + CHR_EOT

    # HGET
    def _OPTS_HGET(self, cmd):

        '''

        MCU → HGET#<key>#<field>

        MCU ← 100#<value>@
        MCU ← 201@

        '''

        key = cmd[1]
        field = cmd[2]

        rsp = self.datastore.get(key, field)

        if rsp is not None:
            # return the value
            return RSP_OK + CHR_SEP + str(rsp) + CHR_EOT
        else:
            # return the error code
            return ERR_NULL + CHR_EOT


    # HGETALL
    def _OPTS_HGET_ALL(self, cmd):

        '''
        MCU → HGETALL#<key>

        MCU ← 100[#<field-1>#<value-1>#<field-2>#<value-2>]@
        '''

        key = cmd[1]

        rsp_str = RSP_OK

        fields = self.datastore.hgetall(key)
        for field in fields:
            # TODO CHR_SEP deve essere inserito alla fine, e non se la chiave é l'ultima
            rsp_str += CHR_SEP + field + CHR_SEP + fields[field]

        rsp_str += CHR_EOT


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

#start redis connection
#r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

#thread = SerialMonitor("Thread-SerialMonitor")
#thread.start()

serialManager = SerialManager()
serialManager.main()
