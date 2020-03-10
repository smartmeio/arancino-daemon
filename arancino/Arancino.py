
import threading
from threading import Thread
from datetime import datetime, timedelta
from arancino.ArancinoUtils import ArancinoLogger, ArancinoConfig, getProcessUptime
from arancino.discovery.ArancinoSerialDiscovery import ArancinoSerialDiscovery
from arancino.discovery.ArancinoTestDiscovery import ArancinoTestDiscovery
from arancino.ArancinoPortSynchronizer import ArancinoPortSynch
from arancino.port.ArancinoPort import PortTypes
from arancino.ArancinoConstants import ArancinoApiResponseCode
from arancino.ArancinoDataStore import ArancinoDataStore


import signal
import time

# BUG gestire il caso in cui si chiude redis, mentre gira il software. se succede, capita che facendo il kill il software non si interrompe.

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
API_CODE = ArancinoApiResponseCode()
DATASTORE = ArancinoDataStore.Instance()

#@Singleton
class Arancino(Thread):
    _instance = None
    _lock = threading.Lock()
    _init = None


    def __new__(cls):
        if Arancino._instance is None:
            with Arancino._lock:
                if Arancino._instance is None:
                    Arancino._instance = super(Arancino, cls).__new__(cls)
        return Arancino._instance


    def __init__(self):
        if Arancino._instance is not None and not Arancino._init:
            Thread.__init__(self, name='Arancino')

            self.__stop = False
            self.__pause = False
            self.__cycle_time = CONF.get_general_cycle_time()
            self.__version = CONF.get_metadata_version()

            self.__thread_start = None
            self.__thread_start_reset = None

            self.__ports_connected = {}
            self.__ports_discovered = {}

            self.__serial_discovery = ArancinoSerialDiscovery()
            self.__test_discovery = ArancinoTestDiscovery()

            self.__synchronizer = ArancinoPortSynch()

            # signal.signal(signal.SIGINT, self.__kill)
            # signal.signal(signal.SIGTERM, self.__kill)

            self.__uptime_str = ""
            self.__uptime_sec = 0

            Arancino._init = True


    def __kill(self, signum, frame):
        LOG.warning("Killing the Process... ")
        self.__stop = True

    # def __exit___(self):
    #     LOG.info("Starting Exit procedure... ")
    #     LOG.info("Disconnecting Ports... ")
    #     for id, port in self.__ports_connected.items():
    #         port.unplug()
    #
    #     for id, port in self.__ports_discovered.items():
    #         port.unplug()
    #         self.__synchronizer.synchPort(port)
    #
    #     # self.__synchronizer.synchClean(self.__ports_discovered)
    #
    #     LOG.info("Bye!")
    #
    #     # TODO close redis connection
    #
    #     # exit(0)

    def __exit(self):
        LOG.info("Starting Exit procedure... ")
        LOG.info("Disconnecting Ports... ")
        for id, port in self.__ports_connected.items():
            port.unplug()

        for id, port in self.__ports_discovered.items():
            port.unplug()

        LOG.info("Disconnecting Data Stores... ")
        DATASTORE.closeAll()

        LOG.info("Bye!")

        # TODO close redis connection



    def stop(self):
        self.__kill(None, None)


    def run(self):

        self.__thread_start = time.time()
        self.__thread_start_reset = time.time()

        serial_ports = {}
        test_ports = {}

        LOG.info("Arancino version {} Starts!".format(self.__version))

        while not self.__stop:
            if not self.__pause:
                self.__uptime_sec = (time.time() - self.__thread_start)
                self.__uptime_str = getProcessUptime(self.__uptime_sec)
                LOG.info('Uptime :' + self.__uptime_str)

                serial_ports = self.__serial_discovery.getAvailablePorts(serial_ports)
                test_ports = self.__test_discovery.getAvailablePorts(test_ports)

                # works only in python 3.5 and above
                self.__ports_discovered = {**serial_ports, **test_ports}


                LOG.debug('Discovered Ports: ' + str(len(self.__ports_discovered)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_discovered.items()))
                LOG.debug('Connected Ports: ' + str(len(self.__ports_connected)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_connected.items()))

                # log that every hour
                if (time.time() - self.__thread_start_reset) >= 3600:
                    LOG.info('Discovered Ports: ' + str(len(self.__ports_discovered)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_discovered.items()))
                    LOG.info('Connected Ports: ' + str(len(self.__ports_connected)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_connected.items()))
                    #LOG.info('Uptime: ' + str(timedelta(seconds=int(time.time() - self.__thread_start))))
                    LOG.info('Uptime :' + self.__uptime_str)

                    self.__thread_start_reset = time.time()


                # for each discovered port
                for id, port in self.__ports_discovered.items():

                    # discovered port is already a connected port
                    if id in self.__ports_connected:
                        # get the port
                        p_conn = self.__ports_connected[id]
                        # read new configuration
                        self.__synchronizer.readPortConfig(p_conn)
                        self.__synchronizer.writePortChanges(p_conn)

                        # if disabled then disconnect.
                        if not p_conn.isEnabled():
                            p_conn.disconnect()

                    # discovered port in not yet a connected port
                    else:

                        # first time ever this port is plugged: register base informations
                        if not self.__synchronizer.portExists(port=port):
                            # assign a creation date
                            port.setCreationDate(datetime.now())
                            # set default configuration for the port (based on port type)
                            self.__synchronizer.writePortConfig(port)
                            self.__synchronizer.writePortBase(port)
                        else:
                            self.__synchronizer.readPortConfig(port)


                        if port.isFirstTimeLoaded(): ## é la prima volta che la carichi dal db
                            # leggi la creation date
                            # leggi la last usage date (serve leggerla la prima volta perche potrebbe essere disabilitata e quindi non usata)
                            self.__synchronizer.readPortChanges(port)



                        self.__synchronizer.writePortChanges(port)
                        self.__synchronizer.writePortLink(port)
                        self.__synchronizer.writePortStatus(port)
                        self.__synchronizer.writePortInfo(port)

                        if port.isEnabled():

                            try:

                                port.setDisconnectionHandler(self.__disconnectedPortHandler)
                                port.setReceivedCommandHandler(self.__commandReceived)
                                port.connect()
                            except Exception as ex:
                                LOG.exception(ex)


                            # move Arancino Port to the self.__ports_connected
                            self.__ports_connected[id] = port
                        else:
                            LOG.warning("Port is not enabeled, can not connect to: {} - {} at {}".format(port.getAlias(), port.getId(), port.getDevice()))


            time.sleep(int(self.__cycle_time))


        self.__exit()


    # def __retrieveNewPorts(self, discovered):
    #     """
    #     Retrieves new ports to connect to.
    #     Starting from plugged ports, it checks if a port is contained inside
    #     the list of connected ports. It also checks if the port is enabled
    #     and can be connected.
    #
    #     :param discovered: Dict of ArancinoPorts
    #     :param connected: Dict of ArancinoPorts which rappresents the connected ports
    #     :return: List of ArancinoPorts to connect to
    #     """
    #
    #     ports_to_connect = []
    #
    #     try:
    #         for id, port in discovered.items():
    #             if port.getId() not in self.__ports_connected:
    #                     if port.isEnabled():
    #                         # if true: there'are new plugged ports discovered
    #                         ports_to_connect.append(port)
    #                     else:
    #                         LOG.warning("Port {} {} at {} is Not Enabled".format(port.getId(), port.getAlias(), port.getDevice()))
    #
    #     except Exception as ex:
    #         LOG.exception(ex)
    #
    #     return ports_to_connect
    #
    #
    # def __disconnectDisabledPorts(self, connected):
    #     """
    #     Cycles all the connected ports and puts the disabled ones into
    #     disabled_ports List. Finally it returns disabled_ports
    #
    #     :param connected: Dict of Connected Ports
    #     :param discovered: Dict of Discovered Ports
    #     :return disabled_ports: a list of Disabled Port
    #
    #     """
    #     try:
    #         for id, port in connected.items():
    #             if port is not None and not port.isEnabled():
    #                 #disabled_ports.append(port)
    #                 port.disconnect()
    #
    #     except Exception as ex:
    #         LOG.exception(ex)
    #
    #
    # def __connectPorts(self, ports_to_connect):
    #     """
    #     TODO redo this docs
    #     Gets ports from ports_to_connect List and check if they are enabled.
    #         If enabled first attachs the disconnection handler and then invokes the connect method.
    #         Then move the ArancinoPort to the self.__port_connected Dict
    #
    #
    #     For each ports in ports_to_connect List, creates a new instance of Serial Connector and starts it.
    #     Serial Connector instance is stored into a List of connected port using the
    #     serial number of the port as key for the List
    #
    #     :param ports_to_connect: List of ArancinoPort
    #     :return ports_connected: Dictionary of SerialConnector
    #     """
    #
    #     try:
    #
    #         for port in ports_to_connect:
    #
    #             if port.isEnabled():
    #
    #                 port.setDisconnectionHandler(self.__disconnectedPortHandler)
    #                 port.setReceivedCommandHandler(self.__commandReceived)
    #                 port.connect()
    #
    #                 # move Arancino Port to the self.__ports_connected
    #                 self.__ports_connected[port.getId()] = port
    #
    #
    #             else:
    #                 LOG.warning("Port is not enabeled, can not connect to: {} {} at {}".format(port.getAlias(), port.getId(), port.getDevice()))
    #
    #     except Exception as ex:
    #         LOG.error(ex)



    def __commandReceived(self, port_id, acmd):
        port = self.__ports_connected[port_id]
        port.setLastUsageDate(datetime.now())


    def __disconnectedPortHandler(self, port_id):

        port = self.__ports_connected.pop(port_id, None)
        LOG.warning("[{} - {} at {}] Destroying Arancino Port".format(port.getPortType(), port.getId(), port.getDevice()))
        #self.__synchronizer.synchPort(port)
        self.__synchronizer.writePortStatus(port)
        # TODO pay attention to that DEL: nel caso dell'upload, viene invocato il disconnect che triggera questo
        #   handler ed infine inoca il DEL. ma nel frattempo tempo essere invocato il run bossa (che impiega diversi secondi)
        #   e poi tornare alla api il ritorno. Se viene fatto il DEL come si comporta?
        del port


    ##### API UTILS ######

    def findPort(self, port_id):
        if port_id in self.__ports_connected:
            return self.__ports_connected[port_id]
        elif port_id in self.__ports_discovered:
            return self.__ports_discovered[port_id]
        else:
            return None

    def pauseArancinoThread(self):
        self.__pause = True
        self.__cycle_time = 1

    def resumeArancinoThread(self):
        self.__cycle_time = CONF.get_general_cycle_time()
        self.__pause = False

    def getUptime(self):
        return self.__uptime_sec

    def getConnectedPorts(self):
        return self.__ports_connected

    def getDiscoveredPorts(self):
        return self.__ports_discovered
