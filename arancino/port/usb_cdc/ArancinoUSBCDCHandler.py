import signal
import subprocess
import threading
import time

from arancino.ArancinoConstants import *
from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.port.ArancinoPort import PortTypes
from arancino.utils.ArancinoUtils import *

LOG = ArancinoLogger.Instance().getLogger()

class ArancinoUSBCDCHandler(threading.Thread):

    def __init__(self, name, serial, id, device, commandReceivedHandler, connectionLostHandler):
        threading.Thread.__init__(self, name=name)
        redis = ArancinoDataStore.Instance()
        self.__datastore = redis.getDataStoreStd()
        self.__serial_port = serial      # the serial port
        self.__name = name          # the name, usually the arancino port id
        self.__id = id
        self.__device = device
        self.__log_prefix = "[{} - {} at {}]".format(PortTypes(PortTypes.USB_CDC).name, self.__id, self.__device)

        self.__commandReceivedHandler = commandReceivedHandler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connectionLostHandler = connectionLostHandler    # handler to be called when a connection is lost or stopped

        self.__partial_command = ""
        self.__stop = False

    def run(self):
        try:
            time.sleep(1.5)  # do il tempo ad Arancino di inserire la porta in lista
            count = 0
            str_data = ""
            p = self.__datastore.pubsub(ignore_subscribe_messages=True)
            p.subscribe(self.__id + '_command')
            self.serial_child = subprocess.Popen(["termux-usb", "-r", "-e", os.path.join(os.path.dirname(__file__), 'port_communication.py'), str(self.__device)], preexec_fn=os.setsid)
            p.get_message()
            time.sleep(5)
            while not self.__stop:
                # Ricezione dati

                self.__partial_command = p.get_message()
                if self.__commandReceivedHandler is not None and self.__partial_command is not None:
                    if self.__partial_command['data'] == 'disconnected':
                        self.__connection_lost()
                        continue
                    self.__commandReceivedHandler(self.__partial_command['data'])
                # clear the handy variables and start again
                self.__partial_command = ""
        except Exception as ex:
            LOG.exception("{}Error on connection lost: {}".format(self.__log_prefix, str(ex)))
            self.__connection_lost()

    def __connection_lost(self):
        '''
        When a connection_lost is triggered means the connection to the serial port is lost or interrupted.
        In this case ArancinoPort (from plugged_ports) must be updated and status information stored into
        the device store.
        '''
        try:

            LOG.warning("{}Connection lost".format(self.__log_prefix))
            if self.__connectionLostHandler is not None:
                self.__connectionLostHandler()


        except Exception as ex:
            LOG.exception("{}Error on connection lost: {}".format(self.__log_prefix, str(ex)))

    def stop(self):
        os.killpg(os.getpgid(self.serial_child.pid), signal.SIGTERM)
        self.__stop = True
