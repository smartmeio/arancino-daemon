
from threading import Thread
from datetime import timedelta
from arancino.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.discovery.ArancinoSerialDiscovery import ArancinoSerialDiscovery
from arancino.ArancinoPortSynchronizer import ArancinoPortSynch
import signal
import time

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()


class ArancinoMain(Thread):

    def __init__(self):
        Thread.__init__(self)

        self.__stop = False
        self.__cycle_time = CONF.get_general_cycle_time()
        self.__version = CONF.get_metadata_version()

        self.__thread_start = None
        self.__thread_start_reset = None

        self.__ports_connected = {}
        self.__ports_discovered = {}

        self.__serial_discovery = ArancinoSerialDiscovery()
        self.__synchronizer = ArancinoPortSynch()

        signal.signal(signal.SIGINT, self.__kill)
        signal.signal(signal.SIGTERM, self.__kill)


    def __kill(self, signum, frame):
        LOG.warning("Received Kill: Exiting... ")
        self.__stop = True

    def __exit(self):

        for id, port in self.__ports_connected.items():
            port.disconnect()


        #TODO close redis connection

        exit(0)


    def run(self):
        # Polls every 10 seconds if there's new port to connect to

        self.__thread_start = time.time()
        self.__thread_start_reset = time.time()

        LOG.info("Arancino version {} Starts!".format(self.__version))

        while not self.__stop:

            self.__ports_discovered = self.__serial_discovery.getAvailablePorts()

            LOG.debug('Discovered Ports: ' + str(len(self.__ports_discovered)) + ' => ' + ' '.join('[' + port.port_type + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_discovered.items()))
            LOG.debug('Connected Ports: ' + str(len(self.__ports_connected)) + ' => ' + ' '.join('[' + port.port_type + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_connected.items()))

            # log that every hour
            if (time.time() - self.__thread_start_reset) >= 3600:
                LOG.info('Discovered Ports: ' + str(len(self.__ports_discovered)) + ' => ' + ' '.join('[' + port.port_type + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_discovered.items()))
                LOG.info('Connected Ports: ' + str(len(self.__ports_connected)) + ' => ' + ' '.join('[' + port.port_type + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_connected.items()))
                LOG.info('Uptime: ' + str(timedelta(seconds=int(time.time() - self.__thread_start))))

                self.__thread_start_reset = time.time()

            # first synchronization in loop
            self.__synchronizer.synchPorts(self.__ports_discovered)

            # retrieve if there are new ports to connect to
            if self.__ports_discovered:

                # this is List (not a Dict) of type ArancinoPort
                ports_to_connect = self.__retrieveNewPorts(self.__ports_discovered)
                # LOG.info("Connectable Serial Ports Retrieved: " + str(len(ports_to_connect)))
                LOG.debug("Connectable Ports Retrieved: " + str(len(ports_to_connect)) + ' => ' + ' '.join('[' + port.port_type + ' - ' + str(port.getId()) + ' at ' + str(port.getDevice()) + ']' for port in ports_to_connect))

                #finally connect the new discovered ports
                if ports_to_connect:
                    self.__connectPorts(ports_to_connect)


            # TODO: verificare quale dei due é migliore, specialmente il secondo caso: come rappresenta giorni e mesi?
            LOG.info('Uptime1:' + self.__getProcessUptime((time.time() - self.__thread_start)))
            LOG.info('Uptime2:' + str(timedelta(seconds=int(time.time() - self.__thread_start))))

            # second synchronization in loop
            self.__synchronizer.synchPorts(self.__ports_discovered)

            # print stats
            #self.__printStats()

            time.sleep(int(self.__cycle_time))
            #time.sleep(int(1000))


        self.__exit()


    def __retrieveNewPorts(self, discovered):
        """
        Retrieves new ports to connect to.
        Starting from plugged ports, it checks if a port is contained inside
        the list of connected ports. It also checks if the port is enabled
        and can be connected.

        :param discovered: Dict of ArancinoPorts
        :param connected: Dict of ArancinoPorts which rappresents the connected ports
        :return: List of ArancinoPorts to connect to
        """

        ports_to_connect = []

        try:
            for id, port in discovered.items():
                if port.getId() not in self.__ports_connected:
                        if port.isEnabled():
                            # if true: there'are new plugged ports discovered
                            ports_to_connect.append(port)
                        else:
                            LOG.warning("Port {} {} at {} is Not Enabled".format(port.getId(), port.getAlias(), port.getDevice()))

        except Exception as ex:
            LOG.exception(ex)

        return ports_to_connect


    def __connectPorts(self, ports_to_connect):
        """
        TODO redo this docs
        Gets ports from ports_to_connect List and check if they are enabled.
            If enabled first attachs the disconnection handler and then invokes the connect method.
            Then move the ArancinoPort to the self.__port_connected Dict


        For each ports in ports_to_connect List, creates a new instance of Serial Connector and starts it.
        Serial Connector instance is stored into a List of connected port using the
        serial number of the port as key for the List

        :param ports_to_connect: List of ArancinoPort
        :return ports_connected: Dictionary of SerialConnector
        """

        try:

            for port in ports_to_connect:

                if port.isEnabled():

                    port.setDisconnectionHandler(self.__disconnectedPortHandler)
                    port.connect()

                    # move Arancino Port to the self.__ports_connected
                    self.__ports_connected[port.getId()] = port  # TODO is this passed by value or by reference?


                else:
                    LOG.warning("Port is not enabeled, can not connect to: {} {} at {}".format(port.getAlias(), port.getId(), port.getDevice()))

        except Exception as ex:
            LOG.exception(ex)


    def __disconnectedPortHandler(self, port_id):

        port = self.__ports_connected.pop(port_id, None)
        LOG.warning("[{} - {} at {}] Destroying Arancino Port".format(port.port_type, port.getId(), port.getDevice()))

        del port


    def __printStats(self):
        stats = open(CONF.get_stats_file_path(), "w")
        stats.write("################################ ARANCINO STATS ################################\n")
        stats.write("\n")
        stats.write("ARANCINO UPTIME: " + self.__getProcessUptime((time.time() - self.__thread_start)) + "\n")
        stats.write("ARANCINO VERSION: " + self.__version + "\n")
        stats.write("\n")
        # stats.write("Generic Error - - - - - - - - - - - - - - - - - - - - - - - - - - - - " + str(count_ERR).zfill(10) + "\n")
        # stats.write("Command Not Found - - - - - - - - - - - - - - - - - - - - - - - - - - " + str(count_ERR_CMD_NOT_FND).zfill(10) + "\n")
        # stats.write("Invalid Parameter Number Error- - - - - - - - - - - - - - - - - - - - " + str(count_ERR_CMD_PRM_NUM).zfill(10) + "\n")
        # stats.write("Generic Redis Error - - - - - - - - - - - - - - - - - - - - - - - - - " + str(count_ERR_REDIS).zfill(10) + "\n")
        # stats.write("Key exists in the Standard Data Store Error - - - - - - - - - - - - - " + str(count_ERR_REDIS_KEY_EXISTS_IN_STD).zfill(10) + "\n")
        # stats.write("Key exists in the Persistent Data Store  Error- - - - - - - - - - - - " + str(count_ERR_REDIS_KEY_EXISTS_IN_PERS).zfill(10) + "\n")
        # stats.write("Non compatibility between Arancino Module and Library Error - - - - - " + str(count_ERR_NON_COMPATIBILITY).zfill(10) + "\n")
        stats.write("\n")
        stats.write("################################################################################\n")
        stats.close()


    def __getProcessUptime(self, total_seconds):
        # https://thesmithfam.org/blog/2005/11/19/python-uptime-script/

        # Helper vars:
        MINUTE = 60
        HOUR = MINUTE * 60
        DAY = HOUR * 24

        # Get the days, hours, etc:
        days = int(total_seconds / DAY)
        hours = int((total_seconds % DAY) / HOUR)
        minutes = int((total_seconds % HOUR) / MINUTE)
        seconds = int(total_seconds % MINUTE)

        # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
        string = ""
        if days > 0:
            string += str(days) + " " + (days == 1 and "day" or "days") + ", "
        if len(string) > 0 or hours > 0:
            string += str(hours) + " " + (hours == 1 and "hour" or "hours") + ", "
        if len(string) > 0 or minutes > 0:
            string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes") + ", "
        string += str(seconds) + " " + (seconds == 1 and "second" or "seconds")

        return string
