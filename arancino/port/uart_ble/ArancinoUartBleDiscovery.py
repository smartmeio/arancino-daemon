# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 SmartMe.IO

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

from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from bleak import BleakError

from arancino.port.ArancinoPortFilter import FilterTypes
from arancino.port.uart_ble.ArancinoUartBleService import ArancinoUartBleService
from arancino.utils.ArancinoUtils import ArancinoConfig, ArancinoLogger
from arancino.port.uart_ble.ArancinoUartBlePort import ArancinoUartBlePort
from arancino.port.uart_ble.ArancinoUartBlePortFilter import ArancinoUartBlePortFilter
from threading import Thread, Lock
import time
from arancino.port.ArancinoPort import PortTypes

CONF = ArancinoConfig.Instance()
LOG = ArancinoLogger.Instance().getLogger()


class ArancinoUartBleDiscovery:

    def __init__(self):
        self.__filter = ArancinoUartBlePortFilter()
        self.__filter_type = CONF.get_port_serial_filter_type()
        self.__filter_list = CONF.get_port_serial_filter_list()

        self.__real_list = {}

        self.__ble = BLERadio()

        self.__stop = False
        self.__mutex = Lock()

        self.__th_discovery = Thread(target=self.__discovery)
        #self.__th_clean = Thread(target=self.__stop)

        self.__th_discovery.start()
        #self.__th_clean.start()

        self.__portType = PortTypes.UART_BLE
        self.__log_prefix = "Arancino Discovery {}".format(self.__portType.name)


    def __discovery(self):

        while not self.__stop:

            try:

                adv_list = []
                work_list = {}
                adv_list = self.__ble.start_scan(ProvideServicesAdvertisement, timeout=25)

                # for adv in self.__adv_list:
                #     if UARTService in adv.services and adv.address.string not in self.__work_list:
                #         self.__work_list[adv.address.string] = adv
                for adv in adv_list:
                    if adv.address.string not in work_list:
                        work_list[adv.address.string] = adv

                self.__mutex.acquire()
                self.__real_list = work_list
                self.__mutex.release()
                # print("DISC:")
                # print(self.__real_list)

            except BleakError as er:
                LOG.warning("{}: {}".format(self.__log_prefix, er))
                time.sleep(5)

            except Exception as ex:
                LOG.error("{}: {}".format(self.__log_prefix, er))



        # for adv in self.__ble.start_scan(ProvideServicesAdvertisement):
        #     if not self.__stop:
        #         print("started")
        #         if UARTService in adv.services:
        #             if not adv.address.string in self.__work_list:
        #                 self.__work_list.append(adv.address.string)
        #     else:
        #         print("stopped")
        #         # self.__ble.stop_scan()
        #         # TODO differenze tra real e working list.
        #         self.__real_list = self.__work_list
        #         self.__work_list.clear()
        #         print(self.__real_list)


    def __preFilterPorts(self, ports):
        """
        Pre Filter Serial Ports with valid Serial Number, VID and PID
        :param ports: List of ListPortInfo
        :return ports_filterd: List
        """
        ports_filterd = []

        for id, adv in ports.items():
            if ArancinoUartBleService in adv.services:
                ports_filterd.append(adv)

        return ports_filterd

    def __postFilterPorts(self, ports={}, filter_type=FilterTypes.ALL, filter_list=[]):

        if filter_type == FilterTypes.ONLY:
            return self.__filter.filterOnly(ports, filter_list)

        elif filter_type == FilterTypes.EXCLUDE:
            return self.__filter.filterExclude(ports, filter_list)

        elif filter_type == FilterTypes.ALL:
            return self.__filter.filterAll(ports, filter_list)


    # TODO: this can be an abstract method
    def getAvailablePorts(self, collection):
        """
        Using python-serial library, it scans the serial ports applies filters and then
            returns a Dictionary of ArancinoPort
        :return Dictionary of ArancinoPort
        """
        self.__mutex.acquire()
        ports = self.__real_list
        ports = self.__preFilterPorts(ports)
        ports = self.__transformInArancinoPorts(ports)

        ports = self.__postFilterPorts(ports=ports, filter_type=self.__filter_type, filter_list=self.__filter_list)

        for id, port in ports.items():
            if id not in collection:
                collection[id] = port
            else:
                pass#del collection[id]

        for id in list(collection):
            if id not in ports:
                del collection[id]

        print("AVAIL:")
        print(ports)
        self.__mutex.release()

        del ports
        return collection


    def __transformInArancinoPorts(self, ports):
        """
        This methods creates a new structure starting from a List of ListPortInfo.
        A base element of the new structure is composed by some metadata and
        the initial object of type ListPortInfo


        :param ports: List of plugged port (ListPortInfo)
        :return: Dict of Ports with additional information
        """
        new_ports_struct = {}

        for adv in ports:
            id = adv.address.string
            name = adv.complete_name
            device = self.__ble.name
            p = ArancinoUartBlePort(adv=adv, id=id, device=device, m_c_alias=name, m_s_plugged=True, timeout=CONF.get_port_uart_ble_timeout())
            #p = ArancinoSerialPort(timeout=CONF.get_port_serial_timeout(), port_info=port, m_s_plugged=True, m_c_enabled=CONF.get_port_serial_enabled(), m_c_hide=CONF.get_port_serial_hide(), baudrate_comm=CONF.get_port_serial_comm_baudrate(), baudrate_reset=CONF.get_port_serial_reset_baudrate())
            new_ports_struct[p.getId()] = p

        return new_ports_struct

    def stop(self):
        self.__stop = True
        #self.__th_discovery.stop()