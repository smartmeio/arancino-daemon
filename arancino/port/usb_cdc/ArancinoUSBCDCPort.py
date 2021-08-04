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
import time

from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
from arancino.ArancinoCortex import *
from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.port.usb_cdc.ArancinoUSBCDCHandler import ArancinoUSBCDCHandler
from arancino.port.usb_cdc.serialCDCACM import *
from arancino.utils.ArancinoUtils import ArancinoConfig, ArancinoLogger

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class ArancinoUSBCDCPort(ArancinoPort):

    def __init__(self, port_info=None, device=None, baudrate_comm=9600, baudrate_reset=300, m_s_plugged=False, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None, timeout=None):

        super().__init__(device=device, port_type=PortTypes.USB_CDC, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, upload_cmd="", receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)
        #self.__serial_port = None       # type: serialCDCACM
        self.__port_info = port_info    # type: usblib.DummyDevice
        redis = ArancinoDataStore.Instance()
        self.__datastore = redis.getDataStoreStd()

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

    def sendResponse(self, raw_response):
        """
        Send a Response to the mcu. A Response is bind to a Command. The Response is sent only if the
            Serial Port is Connected.

        :param raw_response: {String} The Response to send back to the MCU.
        :return: void
        """
        if self._m_s_connected:
            self.__datastore.publish(self._id + '_response', raw_response)
        else:  # not connected
            LOG.warning("{} Cannot Sent a Response: Port is not connected.".format(self._log_prefix))
        pass

    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self._m_c_enabled:
                if not self._m_s_connected:
                    try:

                        LOG.info("{} Connecting...".format(self._log_prefix))

                        if CONF.get_port_serial_reset_on_connect():
                            # first resetting
                            self.reset()

                        self.__serial_port = None
                        self.__serial_handler = ArancinoUSBCDCHandler("ArancinoUSBCDCHandler-"+self._id, self.__serial_port, self._id, self._device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
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
            LOG.info("{} Resetting...".format(self._log_prefix))
            self.disconnect()
            self.setEnabled(False)
            # touch to reset
            subprocess.check_output(["termux-usb", "-r", "-e", os.path.join(os.path.dirname(__file__), 'reset_port.py'), str(self._device)]).decode("utf-8")
            time.sleep(3)
            ports_dev_list = json.loads(subprocess.check_output(["termux-usb", "-l"]))

            # retrieve port informations by file descriptor
            for dev_path in ports_dev_list:
                port = lambda:None
                port.__dict__ = json.loads(subprocess.check_output(["termux-usb", "-r", "-e", os.path.join(os.path.dirname(__file__), 'get_port_info.py'), str(dev_path)]).decode("utf-8"))
                if port.iSerialNumber == self._id:
                    self._device = dev_path
                    break
            self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)
            self.setEnabled(True)
            LOG.info("{} Reset".format(self._log_prefix))
            return True
        except Exception as ex:
            #LOG.info("{} Connected".format(self.__log_prefix))
            LOG.exception(self._log_prefix + str(ex))

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
        self._id = port_info.iSerialNumber
        pass

        # SERIAL ARANCINO PORT METADATA

    def getVID(self):
        return self.__m_p_vid


    def getPID(self):
        return self.__m_p_pid


    def getName(self):
        return self.__m_p_name


    def getSerialNumber(self):
        return self.__m_p_serial_number


    def getManufacturer(self):
        return self.__m_p_manufacturer


    def getProduct(self):
        return self.__m_p_product

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
        self.__serial_handler.stop()  #CDC port stopped
        del self.__serial_handler
        LOG.warning("{} USB CDC Port closed.".format(self._log_prefix))
        # check if the disconnection handler callback function is defined
        if self._disconnection_handler is not None:
            self._disconnection_handler(self._id)
        else:  # do nothing
            pass
