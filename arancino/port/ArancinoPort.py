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

from abc import ABCMeta, abstractmethod

from types import FunctionType, MethodType
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor


class ArancinoPort(object):


    __metaclass__ = ABCMeta

    def __init__(self, device=None, m_s_plugged=False, m_c_enabled=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None):

        # BASE ARANCINO METADATA
        self._id = None  # Id is the Serial Number. It will have a value when the Serial Port is connected
        self._device = None          # the plugged tty i.e: /dev/tty.ACM0
        self._port_type = None

        # BASE ARANCINO STATUS METADATA
        self._m_s_plugged = m_s_plugged
        self._m_s_connected = False
        self._m_s_creation_date = None # TODO devono essere ancora gestite
        self._m_s_last_usage = None # TODO devono essere ancora gestite

        # BASE ARANCINO CONFIGURATION METADATA
        self._m_c_enabled = m_c_enabled
        # self._m_c_auto_connect = m_c_auto_connect # TODO remove
        self._m_c_alias = m_c_alias
        self._m_c_hide = m_c_hide

        # SERIAL ARANCINO PORT METADATA
        self._m_p_vid = None
        self._m_p_pid = None
        self._m_p_name = None
        self._m_p_description = None
        self._m_p_hwid = None
        self._m_p_serial_number = None
        self._m_p_location = None
        self._m_p_manufacturer = None
        self._m_p_product = None
        self._m_p_interface = None


        # Command Executor
        # self._executor = ArancinoCommandExecutor(self._id, self._device)

        # CALLBACK FUNCTIONS
        self._received_command_handler = None
        self._disconnection_handler = None
        self.setReceivedCommandHandler(receivedCommandHandler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        self.setDisconnectionHandler(disconnectionHandler)  # this is the handler to be used whene a disconnection event is triggered

    @abstractmethod
    def connect(self):
        """

        :return:
        """
        pass


    @abstractmethod
    def disconnect(self):
        """

        :return:
        """
        pass


    @abstractmethod
    def sendResponse(self, response):
        """
        Send a Response to a "Port". A Response is bind to a Command. The Response is sent only if the
            "Port" is Connected.

        :param response: {String} The Response to send back to the "Port".
        :return: void
        """
        pass


    @abstractmethod
    def reset(self):
        """

        :return:
        """
        pass


    @abstractmethod
    def __commandReceivedHandler(self, raw_command):
        """
        This is an Asynchronous function, and represent the "handler" to be used by an ArancinoHandler implementation to receive data.
            It first receives a Raw Command from the a "Port" (eg. a Serial Port, a Network Port, etc...) , then translate
            it to an ArancinoCommand object and send it back to another callback function

        :param raw_command: the Raw Command received from a "Port"
        :return: void.
        """
        pass


    @abstractmethod
    def __connectionLostHandler(self):
        """
        This is an Asynchronous function, and represent the "handler" to be used by an ArancinoHandler implementation to trigger a disconnection event.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """
        pass


    # BASE ARANCINO METADATA Encapsulators

    def getId(self):
        return self._id

    def getDevice(self):
        return self._device

    def getPortType(self):
        return self._port_type

    # BASE ARANCINO STATUS METADATA Encapsulators

    def isPlugged(self):
        return self._m_s_plugged


    def isConnected(self):
        return self._m_s_connected


    # BASE ARANCINO CONFIGURATION METADATA Encapsulators

    def isEnabled(self):
        return self._m_c_enabled

    # def getAutoConnect(self):
    #     return self._m_c_auto_connect

    def getAlias(self):
        return self._m_c_alias


    def isHidden(self):
        return self._m_c_hide


    # SERIAL ARANCINO PORT METADATA

    def getVID(self):
        return self._m_p_vid


    def getPID(self):
        return self._m_p_pid


    def getName(self):
        return self._m_p_name


    def getDescription(self):
        return self._m_p_description


    def getHWID(self):
        return self._m_p_hwid


    def getSerialNumber(self):
        return self._m_p_serial_number


    def getLocation(self):
        return self._m_p_location


    def getManufacturer(self):
        return self._m_p_manufacturer


    def getProduct(self):
        return self._m_p_product


    def getInterface(self):
        return self._m_p_interface







    def setEnabled(self, enabled):
        self._m_c_enabled = enabled


    def setAutoConnect(self, auto_connect):
        self._m_c_auto_connect = auto_connect


    def setAlias(self, alias):
        self._m_c_alias = alias


    def setHide(self, hide):
        self._m_c_hide = hide


    # Set Handlers

    def setDisconnectionHandler(self, disconnection_handler):
        if isinstance(disconnection_handler, FunctionType) or isinstance(disconnection_handler, MethodType):
            self._disconnection_handler = disconnection_handler
        else:
            self._disconnection_handler = None


    def setReceivedCommandHandler(self, received_command_handler):
        if isinstance(received_command_handler, FunctionType) or isinstance(received_command_handler, MethodType):
            self._received_command_handler = received_command_handler
        else:
            self._received_command_handler = None




class PortTypes:

    Serial = "SERIAL"
    Http = "HTTP"
    Tcp = "TCP"
    Mqtt = "MQTT"
    Bluetooth = "BLUETOOTH"
    Test = "TEST"