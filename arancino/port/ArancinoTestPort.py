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

from arancino.handler.ArancinoTestHandler import ArancinoTestHandler
from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.handler.ArancinoSerialHandler import ArancinoSerialHandler
from arancino.ArancinoCortex import *
from arancino.ArancinoUtils import ArancinoLogger
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
import uuid


LOG = ArancinoLogger.Instance().getLogger()

class ArancinoTestPort(ArancinoPort):
    def __init__(self, id=None, device=None, m_s_plugged=True, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None):
        super().__init__(device=device, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        self._port_type = PortTypes.Test

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
        self._id = id if id  is not None else uuid.uuid1()
        self._m_c_alias = m_c_alias

        self.__stop = False

        self.__log_prefix = "[{} - {} at {}]".format(self._port_type, self._id, self._device)

        self._executor = ArancinoCommandExecutor(self._id, self._device)

    # TODO implement the method in the abstract class:
    # NOTA: per farlo astratto, si deve muovere l'handler nella super classe e chiamarlo con un nome generico ed anche il log prefix

    def __commandReceivedHandler(self, raw_command):
        """
         This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
             It first receives a Raw Command from the Serial Port, then translate it to an ArancinoCommand object
             and send it back to another callback function

         :param raw_command: the Raw Command received from the Serial port
         :return: void.
         """
        try:
            # create an Arancino Comamnd from the raw command
            acmd = ArancinoComamnd(raw_command=raw_command)
            LOG.debug("{} Received: {}: {}".format(self.__log_prefix, acmd.getId(), str(acmd.getArguments())))

            # check if the received command handler callback function is defined
            if self._received_command_handler is not None:
                self._received_command_handler(self._id, acmd)

            # call the Command Executor and get a raw response
            raw_response = self._executor.exec(acmd)

            # create the Arancino Response object
            arsp = ArancinoResponse(raw_response=raw_response)


        # All Arancino Application Exceptions contains an Error Code
        except ArancinoException as ex:
            arsp = ArancinoResponse(rsp_id=ex.error_code, rsp_args=[])
            LOG.error("{} {}".format(self.__log_prefix, str(ex)))

        # Generic Exception uses a generic Error Code
        except Exception as ex:
            arsp = ArancinoResponse(rsp_id=ArancinoCommandErrorCodes.ERR, rsp_args=[])

        finally:

            try:
                # send the response back.
                self.sendRespose(arsp.getRaw())
                LOG.debug("{} Sending: {}: {}".format(self.__log_prefix, arsp.getId(), str(arsp.getArguments())))

            except SerialException as ex:
                LOG.error("{} Error while transmitting a Response: {}".format(self.__log_prefix), str(ex))

    # TODO implement the method in the abstract class:
    # NOTA: per farlo astratto, si deve muovere l'handler nella super classe e chiamarlo con un nome generico ed anche il log prefix
    def __connectionLostHandler(self):
        self._m_s_connected = False

        del self.__test_handler


        LOG.warning("{} Test Port closed.".format(self.__log_prefix))

        # check if the disconnection handler callback function is defined
        if self._disconnection_handler is not None:
            self._disconnection_handler(self._id)
        else:  # do nothing
            pass


    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self._m_c_enabled:
                if not self._m_s_connected:
                    try:

                        LOG.info("{} Connecting...".format(self.__log_prefix))

                        # first resetting
                        self.reset()

                        self.__test_handler = ArancinoTestHandler("ArancinoTestHandler-"+self._id, self._id, self._device, self.__commandReceivedHandler, self.__connectionLostHandler)
                        self._m_s_connected = True
                        self.__test_handler.start()
                        LOG.info("{} Connected".format(self.__log_prefix))



                    except Exception as ex:
                        # TODO: lasciare il raise????
                        LOG.error("{} Error while connecting: {}".format(self.__log_prefix, str(ex)))
                        raise ex

                else:
                    # TODO LOG or EXCPETION
                    LOG.warning("{} Port already connected".format(self.__log_prefix))
                    pass
            else: # not enabled
                #TODO LOG or EXCEPTION
                LOG.warning("{} Port not enabled".format(self.__log_prefix))
                pass

        except Exception as ex:
            raise ex


    # TODO implement the method in the abstract class:
    # NOTA: per farlo astratto, si deve muovere l'handler nella super classe e chiamarlo con un nome generico ed anche il log prefix

    def disconnect(self):
        try:

            # check if the device is already
            if self._m_s_connected:
                self._m_s_connected = False

                self.__test_handler.stop()

            else:
                LOG.debug("{} Already Disconnected".format(self.__log_prefix))


        except Exception as ex:
            raise ex

    def reset(self):
        # Do nothing
        pass

    def sendRespose(self, raw_response):
        # Do nothing
        pass
