
from threading import Thread
from datetime import timedelta
from arancino.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.ArancinoDiscovery import ArancinoSerialDiscovery
from arancino.ArancinoPortSynchronizer import ArancinoPortSynch
import signal
import sys
import time

LOG = ArancinoLogger.Instance().get_logger()
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
        self.__ports_plugged = {}

        self.__serial_discovery = ArancinoSerialDiscovery()
        self.__synchronizer = ArancinoPortSynch()

        signal.signal(signal.SIGINT, self.__kill)
        signal.signal(signal.SIGTERM, self.__kill)


    def __kill(self):
        LOG.warning("Received Kill: Exiting... ")
        self.__stop = True

    def __stop(self):
        # TODO uscita controllata

        exit(0)
        pass


    def __disconnected_port_handler(self, port_id):

        # TODO

        LOG.warning("porta disconnessa {}".format(port_id))


    def run(self):
        # Polls every 10 seconds if there's new port to connect to

        self.__thread_start = time.time()
        self.__thread_start_reset = time.time()

        LOG.info("Version {} Starting!".format(self.__version))

        while not self.__stop:

            self.__ports_plugged = self.__serial_discovery.get_available_ports()

            LOG.debug('Plugged Ports Retrieved: ' + str(len(self.__ports_plugged)) + ' => ' + ' '.join('[' +  port.port_type + ' - ' + str(id) + ' - ' + str(port.get_device()) + ']' for id, port in self.ports_plugged.items()))

            # LOG.info("Connected Serial Ports: " + str(len(self.ports_connected)))
            LOG.debug('Connected Ports: ' + str(len(self.__ports_connected)) + ' => ' + ' '.join('[' +  port.port_type + ' - ' + str(id) + ' - ' + str(port.get_device()) + ']' for id, port in self.__ports_connected.items()))

            # log that every hour
            if (time.time() - self.__thread_start_reset) >= 3600:
                LOG.info('Plugged Ports Retrieved: ' + str(len(self.__ports_plugged)) + ' => ' + ' '.join('[' +  port.port_type + ' - ' + str(id) + ' - ' + str(port.get_device()) + ']' for id, port in self.__ports_plugged.items()))
                LOG.info('Connected Ports: ' + str(len(self.__ports_connected)) + ' => ' + ' '.join('[' +  port.port_type + ' - ' + str(id) + ' - ' + str(port.get_device()) + ']' for id, port in self.__ports_connected.items()))
                LOG.info('Uptime: ' + str(timedelta(seconds=int(time.time() - self.__thread_start))))

                self.__thread_start_reset = time.time()

            self.__synchronizer.synchPorts(self.__ports_plugged)



            time.sleep(int(self.__cycle_time))

    # def __printStats(self):
    #     stats = open(conf.get_stats_file_path(), "w")
    #     stats.write("################################ ARANCINO STATS ################################\n")
    #     stats.write("\n")
    #     stats.write("ARANCINO UPTIME: " + self.__processUptime((time.time() - self.__thread_start)) + "\n")
    #     stats.write("ARANCINO VERSION: " + self.__version + "\n")
    #     stats.write("\n")
    #     stats.write("Generic Error - - - - - - - - - - - - - - - - - - - - - - - - - - - - " + str(count_ERR).zfill(10) + "\n")
    #     stats.write("Command Not Found - - - - - - - - - - - - - - - - - - - - - - - - - - " + str(count_ERR_CMD_NOT_FND).zfill(10) + "\n")
    #     stats.write("Invalid Parameter Number Error- - - - - - - - - - - - - - - - - - - - " + str(count_ERR_CMD_PRM_NUM).zfill(10) + "\n")
    #     stats.write("Generic Redis Error - - - - - - - - - - - - - - - - - - - - - - - - - " + str(count_ERR_REDIS).zfill(10) + "\n")
    #     stats.write("Key exists in the Standard Data Store Error - - - - - - - - - - - - - " + str(count_ERR_REDIS_KEY_EXISTS_IN_STD).zfill(10) + "\n")
    #     stats.write("Key exists in the Persistent Data Store  Error- - - - - - - - - - - - " + str(count_ERR_REDIS_KEY_EXISTS_IN_PERS).zfill(10) + "\n")
    #     stats.write("Non compatibility between Arancino Module and Library Error - - - - - " + str(count_ERR_NON_COMPATIBILITY).zfill(10) + "\n")
    #     stats.write("\n")
    #     stats.write("################################################################################\n")
    #     stats.close()
    #
    # def __processUptime(self, total_seconds):
    #     # https://thesmithfam.org/blog/2005/11/19/python-uptime-script/
    #
    #     # Helper vars:
    #     MINUTE = 60
    #     HOUR = MINUTE * 60
    #     DAY = HOUR * 24
    #
    #     # Get the days, hours, etc:
    #     days = int(total_seconds / DAY)
    #     hours = int((total_seconds % DAY) / HOUR)
    #     minutes = int((total_seconds % HOUR) / MINUTE)
    #     seconds = int(total_seconds % MINUTE)
    #
    #     # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
    #     string = ""
    #     if days > 0:
    #         string += str(days) + " " + (days == 1 and "day" or "days") + ", "
    #     if len(string) > 0 or hours > 0:
    #         string += str(hours) + " " + (hours == 1 and "hour" or "hours") + ", "
    #     if len(string) > 0 or minutes > 0:
    #         string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes") + ", "
    #     string += str(seconds) + " " + (seconds == 1 and "second" or "seconds")
    #
    #     return string

