import threading
from arancino.ArancinoConstants import *
from arancino.utils.ArancinoUtils import *
from arancino.port.ArancinoPort import PortTypes
import paho.mqtt.client as mqtt


LOG = ArancinoLogger.Instance().getLogger()

class ArancinoSerialHandler(threading.Thread):

    def __init__(self, name, serial, id, device, commandReceivedHandler, connectionLostHandler):
        threading.Thread.__init__(self, name=name)
        self.__serial_port = serial      # the serial port
        self.__name = name          # the name, usually the arancino port id
        self.__id = id
        self.__device = device
        self.__log_prefix = "[{} - {} at {}]".format(PortTypes(PortTypes.SERIAL).name, self.__id, self.__device)

        self.__commandReceivedHandler = commandReceivedHandler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connectionLostHandler = connectionLostHandler    # handler to be called when a connection is lost or stopped

        self.__partial_command = ""
        self.__partial_bytes_command = bytearray(b'')
        self.__stop = False

def on_subscribe(client, userdata, mid, granted_qos):
    LOG.info("Subscribed")
def on_message(client, userdata, message):
    LOG.info("message received  ",str(message.payload.decode("utf-8")), "topic",message.topic," retained ",message.retain)
    if message.retain==1:
        print("This is a retained message")

client=mqtt.Client()
client.on_subscribe=on_subscribe
client.on_message=on_message


LOG.info("Subscribing: ")
ret= client.subscribe(("mqtt/python", 2))
LOG.info("Subscribed return=" + str(ret))
