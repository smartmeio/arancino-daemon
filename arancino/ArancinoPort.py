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


class ArancinoPort(object):

    port_type = None

    __metaclass__ = ABCMeta

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
    def __command_received_handler(self, raw_command):
        """
        This is an Asynchronous function, and represent the "handler" to be used by an ArancinoHandler implementation to receive data.
            It first receives a Raw Command from the a "Port" (eg. a Serial Port, a Network Port, etc...) , then translate
            it to an ArancinoCommand object and send it back to another callback function

        :param raw_command: the Raw Command received from a "Port"
        :return: void.
        """
        pass


    @abstractmethod
    def __connection_lost_handler(self):
        """
        This is an Asynchronous function, and represent the "handler" to be used by an ArancinoHandler implementation to trigger a disconnection event.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """
        pass


    @abstractmethod
    def send_response(self, response):
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



class PortTypes:

    Serial = "SERIAL"
    Http = "HTTP"
    Tcp = "TCP"
    Mqtt = "MQTT"
    Bluetooth = "Bluetooth"