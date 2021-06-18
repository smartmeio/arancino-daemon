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
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.ArancinoCortex import *
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class ArancinoUSBCDCPort(ArancinoPort):

    def __init__(self, port_info=None, device=None, baudrate_comm=9600, baudrate_reset=300, m_s_plugged=False, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None, timeout=None):

        #self.__serial_port = None       # type: serialCDCACM
        self.__port_info = port_info    # type: usblib.DummyDevice


        # SERIAL PORT PARAMETER
        self.__comm_baudrate = baudrate_comm
        self.__reset_baudrate = baudrate_reset
        self.__timeout = timeout

        # SERIAL PORT METADATA
        self.__m_p_vid = None
        self.__m_p_pid = None
        self.__m_p_name = None
        #self.__m_p_description = None
        #self.__m_p_hwid = None
        self.__m_p_serial_number = None
        #self.__m_p_location = None
        self.__m_p_manufacturer = None
        #self.__m_p_product = None
        #self.__m_p_interface = None
        self.__m_p_device = None

        self.__populatePortInfo(port_info=self.__port_info)

        self._executor = ArancinoCommandExecutor(port_id=self._id, port_device=self._device, port_type=self._port_type)

        self._compatibility_array = COMPATIBILITY_MATRIX_MOD_SERIAL[str(CONF.get_metadata_version().truncate())]

        # # CALLBACK FUNCTIONS
        # self.setReceivedCommandHandler(receivedCommandHandler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        # self.setDisconnectionHandler(disconnectionHandler)  # this is the handler to be used whene a disconnection event is triggered

        self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)

    def sendResponse(self, response):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def reset(self):
        pass

    def upload(self):
        pass


    def __populatePortInfo(self, port_info=None):
        self.__m_p_vid = "0x{:04X}".format(port_info.idVendor)
        self.__m_p_pid = "0x{:04X}".format(port_info.idProduct)
        self.__m_p_name = port_info.iProduct
        #self.__m_p_description = p.description
        #self.__m_p_hwid = p.hwid
        self.__m_p_serial_number = port_info.iSerialNumber
        #self.__m_p_location = p.location
        self.__m_p_manufacturer = port_info.iManufacturer
        #self.__m_p_product = p.product
        #self.__m_p_interface = p.interface
        pass