# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2020 SmartMe.IO

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

from serial.tools import list_ports

from arancino.port.ArancinoPort import PortTypes
from arancino.utils.ArancinoUtils import ArancinoConfig
from arancino.port.ArancinoPortFilter import FilterTypes
from arancino.port.serial.ArancinoSerialPortFilter import ArancinoSerialPortFilter
from arancino.port.serial.ArancinoSerialPort import ArancinoSerialPort

CONF = ArancinoConfig.Instance().cfg


class ArancinoSerialDiscovery:

    def __init__(self):
        self.__filter = ArancinoSerialPortFilter()
        self.__filter_type = CONF.get("port").get("serial").get("filter_type")
        self.__filter_list = CONF.get("port").get("serial").get("filter_list")

        self.__portType = PortTypes.SERIAL
        self.__log_prefix = "Arancino Discovery {}".format(self.__portType.name)


    # TODO: this can be an abstract method
    def getAvailablePorts(self, collection):
        """
        Using python-serial library, it scans the serial ports applies filters and then
            returns a Dictionary of ArancinoPort
        :return Dictionary of ArancinoPort
        """

        ports = list_ports.comports()
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

        del ports

        return collection


    def __preFilterPorts(self, ports):
        """
        Pre Filter Serial Ports with valid Serial Number, VID and PID
        :param ports: List of ListPortInfo
        :return ports_filterd: List
        """
        ports_filterd = []

        for port in ports:
            if port.serial_number != None and port.serial_number != "FFFFFFFFFFFFFFFFFFFF" and port.vid != None and port.pid != None:
                ports_filterd.append(port)

        return ports_filterd


    def __postFilterPorts(self, ports={}, filter_type=FilterTypes.ALL, filter_list=[]):

        if filter_type == FilterTypes.ONLY.name:
            return self.__filter.filterOnly(ports, filter_list)

        elif filter_type == FilterTypes.EXCLUDE.name:
            return self.__filter.filterExclude(ports, filter_list)

        elif filter_type == FilterTypes.ALL.name:
            return self.__filter.filterAll(ports, filter_list)


    def __transformInArancinoPorts(self, ports):
        """
        This methods creates a new structure starting from a List of ListPortInfo.
        A base element of the new structure is composed by some metadata and
        the initial object of type ListPortInfo


        :param ports: List of plugged port (ListPortInfo)
        :return: Dict of Ports with additional information
        """
        new_ports_struct = {}

        for port in ports:

            f = self.__retrieve_family_by_vid_pid(port)
            if(f is not None):
                p_timeout = CONF.get("port").get("serial").get(f.lower()).get("timeout") or CONF.get("port").get("serial").get("timeout")
                p_enabled = CONF.get("port").get("serial").get(f.lower()).get("auto_enable") or CONF.get("port").get("serial").get("auto_enable") 
                p_hide = CONF.get("port").get("serial").get(f.lower()).get("hide") or CONF.get("port").get("serial").get("hide") 
                p_baudrate=CONF.get("port").get("serial").get(f.lower()).get("comm_baudrate") or CONF.get("port").get("serial").get("comm_baudrate")
                p_baudrate_reset = CONF.get("port").get("serial").get(f.lower()).get("reset_baudrate") or CONF.get("port").get("serial").get("reset_baudrate")
            else:
                p_timeout = CONF.get("port").get("serial").get("timeout")
                p_enabled = CONF.get("port").get("serial").get("auto_enable") 
                p_hide = CONF.get("port").get("serial").get("hide") 
                p_baudrate=CONF.get("port").get("serial").get("comm_baudrate")
                p_baudrate_reset = CONF.get("port").get("serial").get("reset_baudrate")               

            p = ArancinoSerialPort(mcu_family=f, timeout=p_timeout, port_info=port, m_s_plugged=True, m_c_enabled=p_enabled, m_c_hide=p_hide, baudrate_comm=p_baudrate, baudrate_reset=p_baudrate_reset)

            new_ports_struct[p.getId()] = p

        return new_ports_struct

    def __retrieve_family_by_vid_pid(self, port):

        # recupero la coppia vid:pid della porta corrente
        current_vidpid = "{}:{}".format("0x{:04X}".format(port.vid), "0x{:04X}".format(port.pid)).upper()

        # recupero da configurazione l'elenco dei tipi di mcu per il tipo di porta (seriale in questo caso)
        serial_mcu_list = CONF.get("port").get("serial").get("mcu_type_list")

        # per ogni tipo di porta, faccio le verifiche
        for mcu_family in serial_mcu_list:

            # recupero la lista di vid:pid disponibili per il tipo di mcu
            mcu_vidpid_list = CONF.get("port").get("serial").get(mcu_family).get("list")

            if current_vidpid in mcu_vidpid_list:
                return mcu_family.upper()

        return None


    def stop(self):
        pass
