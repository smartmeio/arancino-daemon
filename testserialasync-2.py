import asyncio
import serial_asyncio
import serial
from serial.tools import list_ports

class Output(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        transport.serial.rts = False
        transport.write(b'start#ok@')

    def data_received(self, data):
        print('data received', repr(data))
        #self.transport.close()

    def connection_lost(self, exc): #TODO gestire l'eccezione per evitare che si incricchi la seriale sulla macchina
        print('port closed')
        asyncio.get_event_loop().stop()


from threading import Thread
import time



'''
questo thread serve solo a monitorare i le porte: invcherà un metodo (handler) esterno
'''
class SerialMonitor (Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.ports_plugged = []
        self.ports_connected = []

    def run(self):
        # Polls every 5 seconds if there's new serial port to connect to
        #while(True):
        self.ports_plugged = list(list_ports.grep('2a03:804F'))
        '''
            print('Plugged')
            for port in self.ports_plugged:
                print(port)

            self.ports_to_connect = self.checkDiff(self.ports_plugged, self.ports_connected)
            self.connectPorts(self.ports_to_connect)

            print('Connected')
            for port in self.ports_connected:
                print(port)


            #time.sleep(2)
        '''
            #test
            #connetto alla prima porta
        port1 = self.ports_plugged[0]
        thread1 = SerialConnector("Thread-"+port1.device, port1)
        thread1.start()

        time.sleep(5)

        port2 = self.ports_plugged[1]
        thread2 = SerialConnector("Thread-"+port2.device, port2)
        thread2.start()


    def checkDiff(self, plugged, connected):
        print('checking differences')
        #TODO: effettuare la differenza tra le due liste e tornare la lista di quelle da connettere.
        #TODO: ripulire le liste
        return plugged

    def connectPorts(self, ports_to_connect):
        print('connecting serial ports')
        #TODO: effettuare la connessione alle porte passate in lista.
        for port in ports_to_connect:
            print("ports to connect to: " + port.device)
        #TODO: aggiungere le porte connesse alla relativa lista


class SerialConnector (Thread):
    def __init__(self, name, port):
        Thread.__init__(self)
        self.loop = asyncio.new_event_loop() #.get_event_loop()
        self.port = port
        self.name = name

    def run(self):
        self.coro = serial_asyncio.create_serial_connection(self.loop, Output, self.port.device, baudrate=115200)
        self.loop.run_until_complete(self.coro)
        self.loop.run_forever()
        self.loop.close()

'''
for port in list_ports.grep('2a03:804F'):
    print(port)
'''
print ('---')

thread = SerialMonitor("Thread#1")
thread.start()

#ottengo tutte le porte con vid e pid specifico

#pluggedports = list(list_ports.grep('2a03:804F'))

#print(pluggedports)

#print(pluggedports[0])
#print(pluggedports[0].device)
#print(pluggedports[1])
#print(pluggedports[1].device)
'''
loop = asyncio.get_event_loop()
coro = serial_asyncio.create_serial_connection(loop, Output, pluggedports[0].device, baudrate=250000)
coro2 = serial_asyncio.create_serial_connection(loop, Output, pluggedports[1].device, baudrate=250000)
loop.run_until_complete(coro)
loop.run_until_complete(coro2)
loop.run_forever()
loop.close()
'''

'''
loop2 = asyncio.get_event_loop()
coro2 = serial_asyncio.create_serial_connection(loop2, Output, pluggedports[1].device, baudrate=250000)
loop2.run_until_complete(coro2)
loop2.run_forever()
loop2.close()
'''