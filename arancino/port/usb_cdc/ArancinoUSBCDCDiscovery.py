# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 smartme.IO

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
import json
import os
import subprocess

from arancino.port.ArancinoPortFilter import FilterTypes
from arancino.port.usb_cdc.ArancinoUSBCDCPort import ArancinoUSBCDCPort
from arancino.port.usb_cdc.ArancinoUSBCDCPortFilter import ArancinoUSBCDCPortFilter
from arancino.port.usb_cdc.serialCDCACM import check_is_CDCACM
from arancino.port.usb_cdc.usblib import device_from_fd
from arancino.utils.ArancinoUtils import ArancinoConfig, ArancinoLogger

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class ArancinoUSBCDCDiscovery:

    def __init__(self):


        cmd = CONF.get_port_usb_cdc_discovery_command()
        self.__discovery_command = cmd.split(" ")

        self.__filter = ArancinoUSBCDCPortFilter()
        self.__filter_type = CONF.get_port_usb_cdc_filter_type()
        self.__filter_list = CONF.get_port_usb_cdc_filter_list()


    def getAvailablePorts(self, collection):
        """
        Using python-serial library, it scans the serial ports applies filters and then
            returns a Dictionary of ArancinoPort
        :return Dictionary of ArancinoPort
        """

        try:
            ports = list()

            # get list of file descriptor like: /dev/bus/usb/aaa/bbb
            ports_dev_list = json.loads(subprocess.check_output(self.__discovery_command))

            # retrieve port informations by file descriptor
            for dev_path in ports_dev_list:
                port = lambda:None
                port.__dict__ = json.loads(subprocess.check_output(["termux-usb", "-r", "-e", os.path.join(os.path.dirname(__file__), 'get_port_info.py'), str(dev_path)]).decode("utf-8"))
                print(port.__dict__)
                ports.append((dev_path, port))

            
            ports = self.__preFilterPorts(ports)
            ports = self.__transformInArancinoPorts(ports)
            ports = self.__postFilterPorts(ports=ports, filter_type=self.__filter_type, filter_list=self.__filter_list)


            # update the current collection
            for id, port in ports.items():
                if id not in collection:
                    collection[id] = port
                else:
                    pass#del collection[id]

            for id in list(collection):
                if id not in ports:
                        del collection[id]

        except Exception as ex:
            LOG.error("Something goes wrong while discovering new USB CDC port: {}".format(str(ex)), exc_info=TRACE)


        return collection


    def __preFilterPorts(self, ports):
        """
        Pre Filter USB CDC Ports with valid Serial Number, VID, PID, and CDC (Data / Communication) Class
        :param ports: list of Tuple of File Descriptor and Device
        :return ports_filterd: list of Tuple of File Descriptor and Device
        """
        ports_filterd = []

        for fd, port in ports:
            if port.iSerialNumber != None and port.iSerialNumber != "FFFFFFFFFFFFFFFFFFFF" and port.idVendor != None and port.idProduct != None:
                ports_filterd.append( (fd, port) )

        return ports_filterd


    def __postFilterPorts(self, ports={}, filter_type=FilterTypes.ALL, filter_list=[]):

        if filter_type == FilterTypes.ONLY:
            return self.__filter.filterOnly(ports, filter_list)

        elif filter_type == FilterTypes.EXCLUDE:
            return self.__filter.filterExclude(ports, filter_list)

        elif filter_type == FilterTypes.ALL:
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

        for fd, port in ports:

            p = ArancinoUSBCDCPort(device=fd, timeout=CONF.get_port_serial_timeout(), port_info=port, m_s_plugged=True, m_c_enabled=CONF.get_port_serial_enabled(), m_c_hide=CONF.get_port_serial_hide(), baudrate_comm=CONF.get_port_serial_comm_baudrate(), baudrate_reset=CONF.get_port_serial_reset_baudrate())
            new_ports_struct[p.getId()] = p

        return new_ports_struct
