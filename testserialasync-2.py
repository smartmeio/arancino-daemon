import asyncio
import serial_asyncio
import serial
from serial.tools import list_ports

from oslo_log import log as logging
LOG = logging.getLogger(__name__)

class SerialHandler(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        transport.serial.rts = False
        transport.write(b'start#ok@')

    def data_received(self, data):
        print('data received', repr(data))
        #self.transport.close()

    def connection_lost(self, exc): #TODO gestire l'eccezione per evitare che si incricchi la seriale sulla macchina
        print('port closed ' + self.transport.serial.name)
        ports_connected.pop(self.transport.serial.name)
        asyncio.get_event_loop().stop()



from threading import Thread
import time

# contains all the plugged ports with a specific vid and pid. Object of type Serial.Port
ports_plugged = []

# contains all the connected serial ports. Object of type Thread - SerialConnector
ports_connected = {}

'''
This thread polls serial ports which match with a specifici pid and vid and then connect to them.
'''
class SerialMonitor (Thread):
    def __init__(self, name):
        Thread.__init__(self)

        #sets the vendor and product ID to check when poll
        self.vid = '2a03'
        self.pid = '804F'
        self.match = self.vid + ':' + self.pid

    def run(self):
        # Polls every 5 seconds if there's new serial port to connect to
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
            thread_serial = SerialConnector("Thread-" + port.device, port)
            thread_serial.start()
            ports_connected[port.device] = thread_serial

class SerialConnector (Thread):
    def __init__(self, name, port):
        Thread.__init__(self)
        self._loop = asyncio.new_event_loop()
        self.port = port
        self.thread_name = name
        self.baudrate = 250000

    def run(self):
        self.coro = serial_asyncio.create_serial_connection(self._loop, SerialHandler, self.port.device, baudrate=self.baudrate)
        self._loop.run_until_complete(self.coro)
        self._loop.run_forever()
        self._loop.close()


thread = SerialMonitor("Thread-SerialMonitor")
thread.start()