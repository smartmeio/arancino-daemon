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

import serial, time
from serial import SerialException

from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.handler.ArancinoSerialHandler import ArancinoSerialHandler
from arancino.ArancinoCortex import *
from arancino.ArancinoUtils import ArancinoLogger
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor


LOG = ArancinoLogger.Instance().getLogger()

class ArancinoTestPort(ArancinoPort):
    def __init__(self, device=None, m_s_plugged=True, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None):
        super(device=device, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_auto_connect=m_c_auto_connect, m_c_alias=m_c_alias, m_c_hide=m_c_hide, receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        self.port_type = PortTypes.Test

        self.__populatePortInfo(device=self.__device, port_info=self.__port_info)

    def __commandReceivedHandler(self):
        pass

    def __connectionLostHandler(self):
        pass

    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self.__m_c_enabled:
                if not self.__m_s_connected:
                    try:

                        # first resetting
                        self.reset()


                        LOG.info("{} Connecting...".format(self._log_prefix))
                        # TODO START THE TEST HANDLER
                        #self.__serial_handler = ArancinoSerialHandler("ArancinoSerialHandler", self.__serial_port, self.__id, self.__device, self.__commandReceivedHandler, self.__connectionLostHandler)
                        self.__m_s_connected = True

                        LOG.info("{} Connected".format(self._log_prefix))

                    except Exception as ex:
                        # TODO: lasciare il raise????
                        LOG.error("{} Error while connecting: {}".format(self._log_prefix), str(ex))
                        raise ex

                else:
                    # TODO LOG or EXCPETION
                    LOG.warning("{} Port already connected".format(self._log_prefix))
                    pass
            else: # not enabled
                #TODO LOG or EXCEPTION
                LOG.warning("{} Port not enabled".format(self._log_prefix))
                pass

        except Exception as ex:
            raise ex

    def disconnect(self):
        pass

    def reset(self):
        pass

    def __populatePortInfo(self):
        self._m_p_vid = "TEST"
        self._m_p_pid = "TEST"
        self._m_p_name = "TEST"
        self._m_p_description = "TEST"
        self._m_p_hwid = "TEST"
        self._m_p_serial_number = "TEST"
        self._m_p_location = "TEST"
        self._m_p_manufacturer = "TEST"
        self._m_p_product = "TEST"
        self._m_p_interface = "TEST"
        self._device = "TEST"
        self._id = "TEST"