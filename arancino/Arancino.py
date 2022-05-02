# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2019 SmartMe.IO

Authors:  Sergio Tomasello <sergio@smartme.io>

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License
"""

from threading import Thread, Lock
from datetime import datetime
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, secondsToHumanString
from arancino.port.serial.ArancinoSerialDiscovery import ArancinoSerialDiscovery
from arancino.port.test.ArancinoTestDiscovery import ArancinoTestDiscovery
from arancino.port.mqtt.ArancinoMqttDiscovery import ArancinoMqttDiscovery
from arancino.port.uart_ble.ArancinoUartBleDiscovery import ArancinoUartBleDiscovery
from arancino.ArancinoPortSynchronizer import ArancinoPortSynch
from arancino.port.ArancinoPort import PortTypes
from arancino.ArancinoConstants import ArancinoApiResponseCode
from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.ArancinoConstants import ArancinoReservedChars

import time

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
API_CODE = ArancinoApiResponseCode()
DATASTORE = ArancinoDataStore.Instance()


#@Singleton
class Arancino(Thread):
    _instance = None
    _lock = Lock()
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
            self.__isPaused = False
            self.__cycle_time = CONF.get_general_cycle_time()
            self.__version = CONF.get_metadata_version()

            LOG.info("Arancino version {} starts on environment {}!".format(self.__version, CONF.get_general_env()))

            self.__thread_start = None
            self.__thread_start_reset = None

            self.__ports_connected = {}
            self.__ports_discovered = {}

            self.__serial_discovery = ArancinoSerialDiscovery() if CONF.get_port_serial_discovery() else None
            self.__test_discovery = ArancinoTestDiscovery() if CONF.get_port_test_discovery() else None
            self.__uart_ble_discovery = ArancinoUartBleDiscovery() if CONF.get_port_uart_ble_discovery() else None
            self.__mqtt_discovery = ArancinoMqttDiscovery()  if CONF.get_port_mqtt_discovery() else None

            self.__serial_ports = {}
            self.__test_ports = {}
            self.__uart_ble_ports = {}
            self.__mqtt_ports = {}

            self.__synchronizer = ArancinoPortSynch()
            self.__datastore = DATASTORE

            # store in datastore: daemon version, daemon environment running mode
            self.__datastore.getDataStoreRsvd().set(ArancinoReservedChars.RSVD_KEY_MODVERSION, str(self.__version))
            self.__datastore.getDataStoreRsvd().set(ArancinoReservedChars.RSVD_KEY_MODENVIRONMENT, CONF.get_general_env())
            self.__datastore.getDataStoreRsvd().set(ArancinoReservedChars.RSVD_KEY_MODLOGLEVEL, CONF.get_log_level())

            # signal.signal(signal.SIGINT, self.__kill)
            # signal.signal(signal.SIGTERM, self.__kill)

            self.__uptime_str = ""
            self.__uptime_sec = 0

            self.__mutex = Lock()

            Arancino._init = True


    def __kill(self, signum, frame):
        LOG.warning("Killing the Process... ")
        self.__stop = True


    def __exit(self):




        LOG.info("Starting Exit procedure... ")

        LOG.info("Disabling Discovery...")
        if CONF.get_port_serial_discovery():
            self.__serial_discovery.stop()

        if CONF.get_port_test_discovery():
            self.__test_discovery.stop()

        if CONF.get_port_uart_ble_discovery():
            self.__uart_ble_discovery.stop()

        LOG.info("Disconnecting Ports... ")
        for id, port in self.__ports_connected.items():
            port.unplug()

        for id, port in self.__ports_discovered.items():
            port.unplug()

        time.sleep(2)
        LOG.info("Disconnecting Data Stores... ")
        time.sleep(3)
        self.__datastore.closeAll()

        LOG.info("Bye!")


    def stop(self):
        self.__kill(None, None)


    def run(self):

        self.__thread_start = time.perf_counter()#time.time()
        # self.__thread_start_reset = time.time()

        if self.__serial_discovery:
            LOG.info("Serial Discovery Enabled")
        else:
            LOG.warning("Serial Discovery Disabled")

        if self.__test_discovery:
            LOG.info("Test Discovery Enabled")
        else:
            LOG.warning("Test Discovery Disabled")

        if self.__uart_ble_discovery:
            LOG.info("UART BLE Discovery Enabled")
        else:
            LOG.warning("UART BLE Discovery Disabled")

        if self.__mqtt_discovery:
            LOG.info("MQTT Discovery Enabled")
        else:
            LOG.warning("MQTT Discovery Disabled")


        while not self.__stop:
            if not self.__pause:
                try:
                    self.__isPaused = False
                    # self.__uptime_sec = (time.time() - self.__thread_start)
                    self.__uptime_sec = (time.perf_counter() - self.__thread_start)
                    self.__uptime_str = secondsToHumanString(self.__uptime_sec)
                    LOG.debug('Uptime :' + str(self.__uptime_sec))
                    LOG.info('Uptime :' + self.__uptime_str)

                    #####################self.__mutex.acquire()

                    # chiama getAvailablePorts solo se il discovery é istanziato (da configurazione)
                    self.__serial_ports = self.__serial_discovery.getAvailablePorts(self.__serial_ports) if self.__serial_discovery else {}
                    self.__test_ports = self.__test_discovery.getAvailablePorts(self.__test_ports) if self.__test_discovery else {}
                    self.__uart_ble_ports = self.__uart_ble_discovery.getAvailablePorts(self.__uart_ble_ports) if self.__uart_ble_discovery else {}
                    self.__mqtt_ports = self.__mqtt_discovery.getAvailablePorts(self.__mqtt_ports) if self.__mqtt_discovery else {}

                    # works only in python 3.5 and above
                    self.__ports_discovered = {**self.__serial_ports, **self.__test_ports, **self.__uart_ble_ports, **self.__mqtt_ports}

                    # # log that every hour
                    # if (time.time() - self.__thread_start_reset) >= 3600:
                    #     LOG.info('Discovered Ports: ' + str(len(self.__ports_discovered)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_discovered.items()))
                    #     LOG.info('Connected Ports: ' + str(len(self.__ports_connected)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_connected.items()))
                    #     #LOG.info('Uptime: ' + str(timedelta(seconds=int(time.time() - self.__thread_start))))
                    #     LOG.info('Uptime :' + self.__uptime_str)
                    #
                    #     self.__thread_start_reset = time.time()


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
                                ###self.__synchronizer.writePortStatus(p_conn)

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

                            if port.isEnabled():

                                try:

                                    port.setDisconnectionHandler(self.__disconnectedPortHandler)
                                    port.setReceivedCommandHandler(self.__commandReceived)
                                    port.connect()
                                except Exception as ex:
                                    pass

                                # move Arancino Port to the self.__ports_connected
                                self.__ports_connected[id] = port
                            else:
                                LOG.warning("Port is not enabled, can not connect to: {} - {} at {}".format(port.getAlias(), port.getId(), port.getDevice()))

                        self.__synchronizer.writePortChanges(port)

                    #####################self.__mutex.release()

                    # for id, port in self.__ports_connected.items():
                    #
                    #     p_conn = self.__ports_connected[id]
                    #
                    #     # Nel caso di uart-ble non c'é un handler di disconnessione
                    #     # quindi si applica un controllo incrociato tra porte
                    #     # connesse e porte discovered. Se la porta é connessa ma
                    #     # non é presente tra le discovered, allora si forza la disconnessione
                    #
                    #     if id not in self.__ports_discovered:
                    #         p_conn.disconnect()
                    #         self.__synchronizer.writePortChanges(port)


                    # elenco delle porte connesse e "started". solo per debug
                    __ports_started = {id:port for (id, port) in self.__ports_connected.items() if port.isStarted()}

                    LOG.debug('Discovered Ports: ' + str(len(self.__ports_discovered)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_discovered.items()))
                    LOG.debug('Connected Ports: ' + str(len(self.__ports_connected)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in self.__ports_connected.items()))
                    LOG.debug('Started Ports: ' + str(len(__ports_started)) + ' => ' + ' '.join('[' + PortTypes(port.getPortType().value).name + ' - ' + str(id) + ' at ' + str(port.getDevice()) + ']' for id, port in __ports_started.items()))



                except Exception as ex:
                    LOG.exception(ex)
            else:
                self.__isPaused = True

            time.sleep(self.__cycle_time)


        self.__exit()


    def __commandReceived(self, port_id, acmd):
        if port_id in self.__ports_connected:
            port = self.__ports_connected[port_id]
            port.setLastUsageDate(datetime.now())


    def __disconnectedPortHandler(self, port_id):
        self.__mutex.acquire()

        # with self.acquire_timeout(self.__mutex, 12) as acquired:
        #     if acquired:
        #         LOG.debug("Lock Acquired")
        if port_id in self.__ports_connected:
            port = self.__ports_connected.pop(port_id, None)
            LOG.warning("[{} - {} at {}] Destroying Arancino Port".format(port.getPortType(), port.getId(), port.getDevice()))
            #self.__synchronizer.synchPort(port)
            ###self.__synchronizer.writePortStatus(port)
            # TODO pay attention to that DEL: nel caso dell'upload, viene invocato il disconnect che triggera questo
            #   handler ed infine inoca il DEL. ma nel frattempo tempo essere invocato il run bossa (che impiega diversi secondi)
            #   e poi tornare alla api il ritorno. Se viene fatto il DEL come si comporta?
            del port

        if port_id in self.__ports_discovered:
            port = self.__ports_discovered.pop(port_id, None)
            del port

        if port_id in self.__serial_ports:
            port = self.__serial_ports.pop(port_id, None)
            del port

        if port_id in self.__test_ports:
            port = self.__test_ports.pop(port_id, None)
            del port

        if port_id in self.__uart_ble_ports:
            port = self.__uart_ble_ports.pop(port_id, None)
            del port

        if port_id in self.__mqtt_ports:
                    port = self.__mqtt_ports.pop(port_id, None)
                    self.__mqtt_discovery.remove_port(port)
                    del port
            # else:
            #     LOG.debug("Can't Lock")
            #     self.__mutex.release()

        self.__mutex.release()

    from contextlib import contextmanager
    @contextmanager
    def acquire_timeout(self, lock, timeout):
        result = lock.acquire(timeout=timeout)
        yield result
        if result:
            lock.release()


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

    def isPaused(self):
        return self.__isPaused

    def getUptime(self):
        return self.__uptime_sec

    def getConnectedPorts(self):
        return self.__ports_connected

    def getDiscoveredPorts(self):
        return self.__ports_discovered

    def identifyPort(self, port_id):
        self.__datastore.getDataStoreRsvd().set(ArancinoReservedChars.RSVD_KEY_BLINK_ID, "1")