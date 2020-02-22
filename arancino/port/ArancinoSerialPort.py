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
from types import FunctionType, MethodType
from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.handler.ArancinoSerialHandler import ArancinoSerialHandler
from arancino.ArancinoCortex import *
from arancino.ArancinoUtils import ArancinoLogger
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor

LOG = ArancinoLogger.Instance().getLogger()

class ArancinoSerialPort(ArancinoPort):

    def __init__(self, port_info=None, device=None, baudrate=9600, m_s_plugged=False, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None, timeout=None):

        super().__init__(device=device, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        self._port_type = PortTypes.Serial

        self.__serial_port = None       # type: serial.Serial
        self.__port_info = port_info    # type: serial.tools.ListPortInfo
        # self.__device = device          # the plugged tty i.e: /dev/tty.ACM0
        # self._device = device
        #
        # self.__id = None  # Id is the Serial Number. It will have a value when the Serial Port is connected


        # SERIAL PORT PARAMETER
        self.__baudrate = baudrate
        self.__timeout = timeout

        # ARANCINO PORT METADATA
        # self.__m_p_vid = None
        # self.__m_p_pid = None
        # self.__m_p_name = None
        # self.__m_p_description = None
        # self.__m_p_hwid = None
        # self.__m_p_serial_number = None
        # self.__m_p_location = None
        # self.__m_p_manufacturer = None
        # self.__m_p_product = None
        # self.__m_p_interface = None
        #self.__m_p_device = None

        self.__populatePortInfo(device=self._device, port_info=self.__port_info)

        # log prefix to be print in each log
        self.__log_prefix = "[{} - {} at {}]".format(self._port_type, self._id, self._device)

        # Command Executor
        # self.__executor = ArancinoCommandExecutor(self.__id, self.__device)

        # # ARANCINO STATUS METADATA
        # self.__m_s_plugged = m_s_plugged
        # self.__m_s_connected = False
        #
        # # ARANCINO CONFIGURATION METADATA
        # self.__m_c_enabled = m_c_enabled
        # self.__m_c_auto_connect = m_c_auto_connect
        # self.__m_c_alias = m_c_alias
        # self.__m_c_hide = m_c_hide

        self._executor = ArancinoCommandExecutor(self._id, self._device)

        # # CALLBACK FUNCTIONS
        #self.setReceivedCommandHandler(receivedCommandHandler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        #self.setDisconnectionHandler(disconnectionHandler)  # this is the handler to be used whene a disconnection event is triggered


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
                self.sendResponse(arsp.getRaw())
                #self.__serial_port.write(arsp.getRaw().encode())
                LOG.debug("{} Sending: {}: {}".format(self.__log_prefix, arsp.getId(), str(arsp.getArguments())))

            except SerialException as ex:
                LOG.error("{} Error while transmitting a Response: {}".format(self.__log_prefix), str(ex))


    def __connectionLostHandler(self):
        """
        This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """
        # TODO se la disconnessione viene gestita al livello superiore facendo una del
        #  di questo oggetto non ha senso impostare connected = false e via dicendo

        self._m_s_connected = False

        # free the handler and serial port
        self.__serial_port.close()

        del self.__serial_handler
        del self.__serial_port

        LOG.warning("{} Serial Port closed.".format(self.__log_prefix))

        # check if the disconnection handler callback function is defined
        if self._disconnection_handler is not None:
            self._disconnection_handler(self._id)
        else:  # do nothing
            pass


    def __populatePortInfo(self, device=None, port_info=None):
        try:
            if device is not None:
                p = self.__findPortInfo(device=device)
            elif port_info is not None:
                p = port_info
            else:
                #TODO To be tested
                raise Exception("Cannot create Arancino Serial Port: Device and Port Info are None, please fill one of them")


            # from serial.tools import list_ports
            # ports = list_ports.comports()
            # for p in ports:
            #     if p.device == device:
                    # sets Port Metadata
            self._m_p_vid = "0x{:04X}".format(p.vid)   #str(hex(p.vid))
            self._m_p_pid = "0x{:04X}".format(p.pid)
            self._m_p_name = p.name
            self._m_p_description = p.description
            self._m_p_hwid = p.hwid
            self._m_p_serial_number = p.serial_number
            self._m_p_location = p.location
            self._m_p_manufacturer = p.manufacturer
            self._m_p_product = p.product
            self._m_p_interface = p.interface
            self._device = p.device

            self._id = p.serial_number

                    # break  # break the whole loop

        except Exception as ex:
            raise ex


    def __findPortInfo(self, device=None):
        from serial.tools import list_ports
        ports = list_ports.comports()
        for p in ports:
            if p.device == device:
                return p


    # APIs

    def sendResponse(self, raw_response):
        """
        Send a Response to the mcu. A Response is bind to a Command. The Response is sent only if the
            Serial Port is Connected.

        :param raw_response: {String} The Response to send back to the MCU.
        :return: void
        """

        if self._m_s_connected:
            self.__serial_port.write(raw_response.encode())
        else:  # not connected
            LOG.warning("{} Cannot Sent a Response: Port is not connected.".format(self.__log_prefix))



    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self._m_c_enabled:
                if not self._m_s_connected:
                    try:

                        LOG.info("{} Connecting...".format(self.__log_prefix))

                        # first resetting
                        self.reset()

                        self.__serial_port = serial.Serial(None, self.__baudrate, timeout=self.__timeout)
                        self.__serial_port.port = self._device
                        self.__serial_port.open()

                        self.__serial_handler = ArancinoSerialHandler("ArancinoSerialHandler-"+self._id, self.__serial_port, self._id, self._device, self.__commandReceivedHandler, self.__connectionLostHandler)
                        self._m_s_connected = True
                        self.__serial_handler.start()
                        LOG.info("{} Connected".format(self.__log_prefix))

                    except Exception as ex:
                        # TODO LOG SOMETHING OR NOT?
                        LOG.error("{} Error while connecting: {}".format(self.__log_prefix, str(ex)))
                        raise ex

                else:
                    # TODO LOG or EXCPETION
                    LOG.warning("{} Port already connected".format(self.__log_prefix))

            else: # not enabled
                #TODO LOG or EXCEPTION
                LOG.warning("{} Port not enabled".format(self.__log_prefix))
                pass

        except Exception as ex:
            raise ex


    def disconnect(self):
        try:
            # check if the device is already
            if self._m_s_connected:
                self._m_s_connected = False

                self.__serial_handler.stop()

            else:
                LOG.debug("{} Already Disconnected".format(self.__log_prefix))


        except Exception as ex:
            raise ex


    def reset(self):
        try:
            LOG.debug("{} Resetting...".format(self.__log_prefix))
            # touch to reset
            ser = serial.Serial()
            ser.baudrate = 300 # TODO make it an attribute
            ser.port = self._device
            ser.open()
            ser.close()
            del ser
            time.sleep(3)
            LOG.debug("{} Reset".format(self.__log_prefix))
        except Exception as ex:
            #LOG.info("{} Connected".format(self.__log_prefix))
            LOG.exception(self.__log_prefix + str(ex))

