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
from adafruit_ble.services.nordic import UARTService

from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.port.serial.ArancinoSerialHandler import ArancinoSerialHandler
from arancino.ArancinoCortex import *
from arancino.port.uart_ble.ArancinoUartBleHandler import ArancinoUartBleHandler
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
from adafruit_ble import BLERadio
import time


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class ArancinoUartBlePort(ArancinoPort):

    def __init__(self, adv=None, id=None, device=None, m_s_plugged=False, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None, timeout=None):

        super().__init__(id=id, device=device, port_type=PortTypes.UART_BLE, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, upload_cmd=CONF.get_port_serial_upload_command(), receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        # self._port_type = PortTypes.Serial

        self.__ble_connection = None    # type: BLEConnection
        self.__ble_uart_service = None
        self.__adv = adv                # type: adafruit_ble.advertising.Advertisement

        # UART BLE PORT
        self.__timeout = timeout



        self._executor = ArancinoCommandExecutor(port_id=self._id, port_device=self._device, port_type=self._port_type)

        self._compatibility_array = COMPATIBILITY_MATRIX_MOD_SERIAL[str(CONF.get_metadata_version().truncate())]

        # # CALLBACK FUNCTIONS
        #self.setReceivedCommandHandler(receivedCommandHandler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        #self.setDisconnectionHandler(disconnectionHandler)  # this is the handler to be used whene a disconnection event is triggered

        self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)

    # def __commandReceivedHandler(self, raw_command):
    #     """
    #     This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
    #         It first receives a Raw Command from the Serial Port, then translate it to an ArancinoCommand object
    #         and send it back to another callback function
    #
    #     :param raw_command: the Raw Command received from the Serial port
    #     :return: void.
    #     """
    #     try:
    #         # create an Arancino Comamnd from the raw command
    #         acmd = ArancinoComamnd(raw_command=raw_command)
    #         LOG.debug("{} Received: {}: {}".format(self._log_prefix, acmd.getId(), str(acmd.getArguments())))
    #
    #         # check if the received command handler callback function is defined
    #         if self._received_command_handler is not None:
    #             self._received_command_handler(self._id, acmd)
    #
    #         # call the Command Executor and get a raw response
    #         raw_response = self._executor.exec(acmd)
    #
    #         # create the Arancino Response object
    #         arsp = ArancinoResponse(raw_response=raw_response)
    #
    #
    #     # All Arancino Application Exceptions contains an Error Code
    #     except ArancinoException as ex:
    #
    #         if ex.error_code == ArancinoCommandErrorCodes.ERR_NON_COMPATIBILITY:
    #             self._setComapitibility(False)
    #
    #         arsp = ArancinoResponse(rsp_id=ex.error_code, rsp_args=[])
    #         LOG.error("{} {}".format(self._log_prefix, str(ex)))
    #
    #     # Generic Exception uses a generic Error Code
    #     except Exception as ex:
    #         arsp = ArancinoResponse(rsp_id=ArancinoCommandErrorCodes.ERR, rsp_args=[])
    #         LOG.error("{} {}".format(self._log_prefix, str(ex)))
    #
    #     finally:
    #
    #         try:
    #             # move there that, becouse if there's an non compatibility error, lib version will not setted
    #             #  moving that in the finally, it will be setted
    #             if acmd.getId() == ArancinoCommandIdentifiers.CMD_SYS_START["id"]:
    #
    #                 self._retrieveStartCmdArgs(acmd.getArguments())
    #
    #                 # if it is not compatible an error was send back to the mcu and the communnication is not started (the mcu receive an errore and try to connect again)
    #                 # if it is compatible the communication starts and it ready to receive new commands.
    #                 started = True if self.isCompatible() else False
    #                 self._setStarted(started)
    #
    #             # send the response back.
    #             self.sendResponse(arsp.getRaw())
    #             LOG.debug("{} Sending: {}: {}".format(self._log_prefix, arsp.getId(), str(arsp.getArguments())))
    #
    #         except SerialException as ex:
    #             LOG.error("{} Error while transmitting a Response: {}".format(self._log_prefix), str(ex))
    #

    def __connectionLostHandler(self):
        """
        This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """
        # # TODO se la disconnessione viene gestita al livello superiore facendo una del
        # #  di questo oggetto non ha senso impostare connected = false e via dicendo
        #
        # self._m_s_connected = False
        # # self._m_s_plugged = False
        #
        # # free the handler and serial port
        # self.__serial_port.close()
        #
        # del self.__serial_handler
        # del self.__serial_port
        #
        # LOG.warning("{} Serial Port closed.".format(self._log_prefix))
        #
        # # check if the disconnection handler callback function is defined
        # if self._disconnection_handler is not None:
        #     self._disconnection_handler(self._id)
        # else:  # do nothing
        #     pass


    # PORT APIs IMPLEMENTATION

    def sendResponse(self, raw_response):
        """
        Send a Response to the mcu. A Response is bind to a Command. The Response is sent only if the
            Serial Port is Connected.

        :param raw_response: {String} The Response to send back to the MCU.
        :return: void
        """

        if self._m_s_connected:
            self.__ble_uart_service.write(raw_response.encode())
        else:  # not connected
            LOG.warning("{} Cannot Sent a Response: Port is not connected.".format(self._log_prefix))


    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self._m_c_enabled:
                if not self._m_s_connected:
                    try:

                        LOG.info("{} Connecting...".format(self._log_prefix))

                        if CONF.get_port_uart_ble_reset_on_connect():
                            # first resetting
                            self.reset()


                        self.__ble_connection = BLERadio().connect(self.__adv, timeout=self.__timeout)
                        self.__ble_uart_service = self.__ble_connection[UARTService]

                        self.__uart_ble_handler = ArancinoUartBleHandler("ArancinoSerialHandler-"+self._id, self.__ble_connection, self._id, self._device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
                        self._m_s_connected = True
                        self.__uart_ble_handler.start()
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

                self.__uart_ble_handler.stop()

            else:
                LOG.debug("{} Already Disconnected".format(self._log_prefix))


        except Exception as ex:
            raise ex


    def reset(self):
        try:

            LOG.info("{} Resetting...".format(self._log_prefix))
            # TODO implementare il reset:
            # Il reset va implementato basandoci su core NRF52 che abbiamo
            # modificato perche all'interno abbbiamo o metteremo un comando speciale
            # per eseguire il reset.

            LOG.info("{} Reset".format(self._log_prefix))
            return True
        except Exception as ex:
            #LOG.info("{} Connected".format(self.__log_prefix))
            LOG.exception(self._log_prefix + str(ex))


    def upload(self, firmware):

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
