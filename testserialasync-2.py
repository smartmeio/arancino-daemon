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
            return self._OPTS_SET(cmd[1], cmd[2])
        #GET
        elif cmd[0] == CMD_APP_GET:
            return self._OPTS_GET(cmd[1])

        #DEL
        elif cmd[0] == CMD_APP_DEL:
            idx = len(cmd)
            return self._OPTS_DEL(cmd[1:idx])

        #KEYS
        elif cmd[0] == CMD_APP_KEYS:
            if len(cmd) == 2:
                return self._OPTS_KEYS(cmd[1]) # w/ pattern
            else:
                return self._OPTS_KEYS() # w/o pattern



    #SET
    def _OPTS_SET(self, key, value):
        print('set ' + key + ' ' + value)

        rsp = self.datastore.set(key, value)
        if rsp:
            # return back the value
            return RSP_OK + CHR_SEP + str(value) + CHR_EOT
        else:
            # return the error code
            return RSP_KO + CHR_SEP + ERR_SET + CHR_EOT


    #GET
    def _OPTS_GET(self, key):
        print('get ' + key)
        value = self.datastore.get(key)

        if value is not None:
            # return the value
            return RSP_OK + CHR_SEP + str(value) + CHR_EOT
        else:
            # return the error code
            return RSP_KO + CHR_SEP + ERR_NOT_AVAIL + CHR_EOT


    #DEL
    def _OPTS_DEL(self, keys):
        print('del ' + keys)
        value = self.datastore.delete(*keys)
        return RSP_OK + CHR_SEP + str(value) + CHR_EOT


    #KEYS
    def _OPTS_KEYS(self, pattern='*'):
        print('key pattern ' + pattern)
        value = self.datastore.keys(pattern)

        if len(value) == 0:
            return RSP_KO + CHR_SEP + ERR_NOT_FOUND + CHR_EOT
        else:
            rsp_str = RSP_OK

            for key in value:
                rsp_str += CHR_SEP + key

            return rsp_str + CHR_EOT


CHR_EOT = chr(4)        #End Of Transmission Char
CHR_SEP = chr(30)       #Separator Char
CMD_SYS_START = 'START' #Start Commmand
CMD_APP_GET = 'GET'     #Get Commmand
CMD_APP_SET = 'SET'     #Set Commmand
CMD_APP_DEL = 'DEL'     #Delete Command
CMD_APP_KEYS = 'DEL'    #Keys Command
RSP_OK = 'OK'           #OK Response
RSP_KO = 'KO'           #KO Response
ERR_NOT_AVAIL = '001'   #Not Available Response Code
ERR_SET = '002'         #Error during SET
ERR_NOT_FOUND = '003'   #Not Found

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
