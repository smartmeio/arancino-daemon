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
from enum import Enum

from types import FunctionType, MethodType

class ArancinoPort(object):


    __metaclass__ = ABCMeta

    def __init__(self, device=None, m_s_plugged=False, m_c_enabled=True, m_c_alias="", m_c_hide=False, port_type=None, upload_cmd=None, receivedCommandHandler=None, disconnectionHandler=None):

        # BASE METADATA
        self._id = None                 # Id is the Serial Number. It will have a value when the Serial Port is connected
        self._device = device           # the plugged tty or ip adddress, i.e: "/dev/tty.ACM0"
        self._port_type = port_type     # Type of port, i.e: Serial, Network, etc...
        self._library_version = None
        self._m_b_creation_date = None


        # BASE STATUS METADATA
        self._m_s_plugged = m_s_plugged
        self._m_s_connected = False
        self._m_s_last_usage_date = None

        # BASE CONFIGURATION METADATA
        self._m_c_enabled = m_c_enabled
        self._m_c_alias = m_c_alias
        self._m_c_hide = m_c_hide

        # OTHER
        self._upload_cmd = upload_cmd

        # Command Executor
        # self._executor = ArancinoCommandExecutor(self._id, self._device)

        # CALLBACK FUNCTIONS
        self._received_command_handler = None
        self._disconnection_handler = None
        self.setReceivedCommandHandler(receivedCommandHandler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        self.setDisconnectionHandler(disconnectionHandler)  # this is the handler to be used whene a disconnection event is triggered


        self.__first_time = True

    def unplug(self):
        self.disconnect()
        self._m_s_plugged = False


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
    def upload(self, firmware):
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


    # BASE METADATA Encapsulators

    def getId(self):
        return self._id


    def _setId(self, id):
        self._id(id)


    def getDevice(self):
        return self._device


    def _setDevice(self, device):
        self._device = device


    def getPortType(self):
        return self._port_type


    def _setPortType(self, port_type):
        self._port_type = port_type


    def getLibVersion(self):
        return self._library_version


    def _setLibVersion(self, library_version):
        self._library_version = library_version


    def getCreationDate(self):
        return self._m_b_creation_date


    def setCreationDate(self, creation_date):
        self._m_b_creation_date = creation_date


    def getLastUsageDate(self):
        return self._m_s_last_usage_date


    def setLastUsageDate(self, last_usage_date):
        self._m_s_last_usage_date = last_usage_date


    # BASE STATUS METADATA Encapsulators

    def isPlugged(self):
        return self._m_s_plugged


    def isConnected(self):
        return self._m_s_connected


    # BASE CONFIGURATION METADATA Encapsulators

    def isEnabled(self):
        return self._m_c_enabled


    def setEnabled(self, enabled):
        self._m_c_enabled = enabled

    # def getAutoConnect(self):
    #     return self._m_c_auto_connect

    def getAlias(self):
        return self._m_c_alias


    def setAlias(self, alias):
        self._m_c_alias = alias


    def isHidden(self):
        return self._m_c_hide


    def setHide(self, hide):
        self._m_c_hide = hide


    def isFirstTimeLoaded(self):
        if(self.__first_time):
            self.__first_time = False
            return True
        else:
            return False


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




class PortTypes(Enum):

    SERIAL = 1        # Serial
    NETWORK = 2       # Wi-Fi or Ethernet Http connection
    TCP = 3           # TCP Socket
    MQTT = 4          # Network MQTT
    BLUETOOTH = 5     # Bluetooth
    TEST = 6          # Fake Port for Test purpose