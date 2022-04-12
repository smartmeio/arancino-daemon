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

import serial
from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.port.serial.ArancinoSerialHandler import ArancinoSerialHandler
from arancino.ArancinoCortex import *
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoConfig2, ArancinoEnvironment
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
import time


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig2.Instance().cfg
TRACE = CONF.get("general").get("trace")
ENV = ArancinoEnvironment.Instance()

class ArancinoSerialPort(ArancinoPort):

    def __init__(self, mcu_family=None, port_info=None, device=None, baudrate_comm=9600, baudrate_reset=300, m_s_plugged=False, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, reset_delay=CONF.get("port").get("serial").get("reset_reconnection_delay"), upload_cmd=CONF.get("port").get("serial").get("upload_command"), receivedCommandHandler=None, disconnectionHandler=None, timeout=None):

        super().__init__(device=device, port_type=PortTypes.SERIAL, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, upload_cmd=upload_cmd, receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        # self._port_type = PortTypes.Serial

        self.__serial_port = None       # type: serial.Serial
        self.__port_info = port_info    # type: serial.tools.ListPortInfo



        # SERIAL PORT PARAMETER
        self.__comm_baudrate = baudrate_comm
        self.__reset_baudrate = baudrate_reset
        self.__timeout = timeout

        # FAMILY PORT PARAMETER
        if mcu_family:
            self._setMicrocontrollerFamily(mcu_family.upper())
        else:
            self.__reset_delay = reset_delay
            self.__upload_command = upload_cmd


        # SERIAL PORT METADATA
        self.__m_p_vid = None
        self.__m_p_pid = None
        self.__m_p_name = None
        self.__m_p_description = None
        self.__m_p_hwid = None
        self.__m_p_serial_number = None
        self.__m_p_location = None
        self.__m_p_manufacturer = None
        self.__m_p_product = None
        self.__m_p_interface = None
        self.__m_p_device = None

        self.__populatePortInfo(device=self._device, port_info=self.__port_info)

        # Command Executor
        # self.__executor = ArancinoCommandExecutor(self.__id, self.__device)

        self._executor = ArancinoCommandExecutor(port_id=self._id, port_device=self._device, port_type=self._port_type)

        self._compatibility_array = COMPATIBILITY_MATRIX_MOD_SERIAL[str(ENV.version.truncate())]

        # # CALLBACK FUNCTIONS
        #self.setReceivedCommandHandler(receivedCommandHandler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        #self.setDisconnectionHandler(disconnectionHandler)  # this is the handler to be used whene a disconnection event is triggered

        self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)



    def __connectionLostHandler(self):
        """
        This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """
        # TODO se la disconnessione viene gestita al livello superiore facendo una del
        #  di questo oggetto non ha senso impostare connected = false e via dicendo

        self._m_s_connected = False
        # self._m_s_plugged = False

        # free the handler and serial port
        self.__serial_port.close()

        del self.__serial_handler
        del self.__serial_port

        LOG.warning("{} Serial Port closed.".format(self._log_prefix))

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
            self.__m_p_vid = "0x{:04X}".format(p.vid)   #str(hex(p.vid))
            self.__m_p_pid = "0x{:04X}".format(p.pid)
            self.__m_p_name = p.name
            self.__m_p_description = p.description
            self.__m_p_hwid = p.hwid
            self.__m_p_serial_number = p.serial_number
            self.__m_p_location = p.location
            self.__m_p_manufacturer = p.manufacturer
            self.__m_p_product = p.product
            self.__m_p_interface = p.interface
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


    # PORT APIs IMPLEMENTATION

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
            LOG.warning("{} Cannot Sent a Response: Port is not connected.".format(self._log_prefix))


    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self._m_c_enabled:
                if not self._m_s_connected:
                    try:

                        LOG.info("{} Connecting...".format(self._log_prefix))

                        if CONF.get("port").get("serial").get("reset_on_connect"):
                            # first resetting
                            self.reset()

                        self.__serial_port = serial.Serial(None, self.__comm_baudrate, timeout=self.__timeout)
                        self.__serial_port.port = self._device
                        self.__serial_port.open()

                        self.__serial_handler = ArancinoSerialHandler("ArancinoSerialHandler-"+self._id, self.__serial_port, self._id, self._device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
                        self._m_s_connected = True
                        self.__serial_handler.start()
                        LOG.info("{} Connected".format(self._log_prefix))
                        self._start_thread_time = time.time()

                    except Exception as ex:
                        # TODO LOG SOMETHING OR NOT?
                        LOG.error("{} Error while connecting: {}".format(self._log_prefix, str(ex)), exc_info=TRACE)
                        raise ex

                else:
                    # TODO LOG or EXCPETION
                    LOG.warning("{} Port already connected".format(self._log_prefix))

            else: # not enabled
                #TODO LOG or EXCEPTION
                LOG.warning("{} Port not enabled".format(self._log_prefix))

        except Exception as ex:
            raise ex


    def disconnect(self):
        try:
            # check if the device is already
            if self._m_s_connected:
                #self._m_s_connected = False

                self.__serial_handler.stop()

            else:
                LOG.debug("{} Already Disconnected".format(self._log_prefix))


        except Exception as ex:
            raise ex


    def reset(self):
        try:

            # if self.getMicrocontrollerFamily():
            #     self._reset_delay = getattr(CONF, "get_port_serial_{}_reset_reconnection_delay()".format(self.getMicrocontrollerFamily().lower()))
            # else:
            #     self._reset_delay = CONF.get_port_serial_reset_reconnection_delay()

            LOG.info("{} Resetting...".format(self._log_prefix))
            self.disconnect()
            self.setEnabled(False)
            # touch to reset
            ser = serial.Serial()
            ser.baudrate = self.__reset_baudrate
            ser.port = self._device
            ser.open()
            ser.close()
            del ser
            #time.sleep( CONF.get_port_serial_reset_reconnection_delay() )
            time.sleep( self.getResetReconnectionDelay())
            self.setEnabled(True)
            LOG.info("{} Reset".format(self._log_prefix))
            return True
        except Exception as ex:
            #LOG.info("{} Connected".format(self.__log_prefix))
            LOG.exception(self._log_prefix + str(ex))


    def upload(self, firmware):

        if self.getMicrocontrollerFamily() == MicrocontrollerFamily.SAMD21:
            LOG.info("{} Starting Upload Procedure".format(self._log_prefix))
            import subprocess

            cmd = self._upload_cmd.format(firmware=firmware, port=self)
            cmd_arr = cmd.split(" ")
            LOG.info("{} Ready to run upload command ===> {} <===".format(self._log_prefix, cmd))

            stdout = None
            stderr = None
            rtcode = 0
            try:
                self.setEnabled(False)
                self.disconnect()
                while self.isConnected():
                    pass

                proc = subprocess.Popen(cmd_arr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = proc.communicate()
                stdout = stdout.decode("utf-8")
                stderr = stderr.decode("utf-8")
                rtcode = proc.returncode

                if rtcode != 0:
                    LOG.error("{} Return code: {} - {}".format(self._log_prefix, str(rtcode), stderr))
                else:
                    LOG.info("{} Upload Success!".format(self._log_prefix))
                    LOG.info("{} {}".format(self._log_prefix, stdout))


            except Exception as ex:
                rtcode = -1
                stderr = str(ex)
                LOG.error("{} Something goes wrong while uploadig: {}".format(self._log_prefix, str(ex)), exc_info=TRACE)

            finally:
                self.setEnabled(True)
                return rtcode, stdout, stderr
        else:
            raise NotImplemented("Upload Function is not available for port {}[{}] of {} Family".format(self.getId(), self.getPortType().name, self.getMicrocontrollerFamily()), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)

    # SERIAL ARANCINO PORT METADATA

    def getVID(self):
        return self.__m_p_vid


    def getPID(self):
        return self.__m_p_pid


    def getName(self):
        return self.__m_p_name


    def getDescription(self):
        return self.__m_p_description


    def getHWID(self):
        return self.__m_p_hwid


    def getSerialNumber(self):
        return self.__m_p_serial_number


    def getLocation(self):
        return self.__m_p_location


    def getManufacturer(self):
        return self.__m_p_manufacturer


    def getProduct(self):
        return self.__m_p_product


    def getInterface(self):
        return self.__m_p_interface

    # SERIAL ARANCINO CONFIG METADATA
    def getResetReconnectionDelay(self):
        return self.__reset_delay

    def setResetReconnectionDelay(self, reset_delay):

        if reset_delay:
            self.__reset_delay = int(reset_delay)