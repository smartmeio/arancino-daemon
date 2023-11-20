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

from arancino.port.ArancinoPortNew import ArancinoPort, PortTypes
from arancino.port.uart_ble.ArancinoUartBleHandler import ArancinoUartBleHandler
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment
from adafruit_ble import BLERadio
import time

from .ArancinoUartBleService import ArancinoUartBleService, ArancinoResetBleService

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("log").get("trace")
ENV = ArancinoEnvironment.Instance()

class ArancinoUartBlePort(ArancinoPort):

    def __init__(
        self, 
        adv=None, 
        id=None, 
        device=None, 
        enabled=True, 
        auto_connect=True, 
        alias="", 
        hide=False, 
        receivedCommandHandler=None, 
        disconnectionHandler=None, 
        timeout=None
    ):

        super().__init__(
            id=id, 
            device=device, 
            port_type=PortTypes.UART_BLE, 
            enabled=enabled, 
            alias=alias, 
            hide=hide, 
            upload_cmd=None, 
            receivedCommandHandler=receivedCommandHandler, 
            disconnectionHandler=disconnectionHandler
        )

        self.__ble_connection = None    # type: BLEConnection
        self.__ble_uart_service = None
        self.__adv = adv                # type: adafruit_ble.advertising.Advertisement

        # UART BLE PORT
        self.__timeout = timeout

        self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)

    def __connectionLostHandler(self):
        """
        This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """
        # # TODO se la disconnessione viene gestita al livello superiore facendo una del
        # #  di questo oggetto non ha senso impostare connected = false e via dicendo
        #

        # free the handler and serial port

        self.disconnect()

        LOG.warning("{} Uart-Ble Port closed.".format(self._log_prefix))

        # check if the disconnection handler callback function is defined
        if self._disconnection_handler is not None:
            self._disconnection_handler(self._id)
        else:  # do nothing
            pass

    # region PORT APIs IMPLEMENTATION

    def sendResponse(self, raw_response):
        """
        Send a Response to the mcu. A Response is bind to a Command. The Response is sent only if the
            Serial Port is Connected.

        :param raw_response: {String} The Response to send back to the MCU.
        :return: void
        """

        if self.is_connected():
            self.__ble_uart_service.write(raw_response)
        else:  # not connected
            LOG.warning("{} Cannot Sent a Response: Port is not connected.".format(self._log_prefix))

    def before_connect(self):
        try:
            # check if the device is enabled and not already connected
            if not self.isEnabled():
                LOG.warning("{} Port already connected".format(self._log_prefix))
                return
        
            if not self.is_connected():
                LOG.error("{} Error while connecting: {}".format(self._log_prefix, str(ex)), exc_info=TRACE)
                raise ex
            
            LOG.info("{} Connecting...".format(self._log_prefix))

            if CONF.get("port").get("uart_ble").get("reset_on_connect"):
                # first resetting
                self.reset()

            self.__ble_connection = BLERadio().connect(self.__adv, timeout=self.__timeout)
            self.__ble_uart_service = self.__ble_connection[ArancinoUartBleService]
            #self.__ble_reset_service = self.__ble_connection[ArancinoResetBleService]

            self.__uart_ble_handler = ArancinoUartBleHandler(self.__ble_connection, self._id, self._device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
            self.__uart_ble_handler.start()
            LOG.info("{} Connected".format(self._log_prefix))
            self._start_thread_time = time.time()
        except Exception as ex:
            raise ex

    def before_disconnect(self):
        try:
            self.__ble_connection.disconnect()

            del self.__uart_ble_handler
            del self.__ble_uart_service
            del self.__adv

            self.stopHeartbeat()

            # check if the device is already
            # if self.is_connected():
            #     self.__uart_ble_handler.stop()
            # else:
            #     LOG.debug("{} Already Disconnected".format(self._log_prefix))


        except Exception as ex:
            raise ex

    def reset(self):
        # No reset provided method for this Port
        #self.__ble_reset_service.reset()
        try:
            self.__ble_connection = BLERadio().connect(self.__adv, timeout=self.__timeout)
            self.__ble_reset_service = self.__ble_connection[ArancinoResetBleService]

            LOG.info("{} Resetting...".format(self._log_prefix))
            self.disconnect()
            self.setEnabled(False)
            # touch to reset
            self.__ble_reset_service.reset()
            
            time.sleep(20)
            self.setEnabled(True)
            LOG.info("{} Reset".format(self._log_prefix))
            return True
        except Exception as ex:
            #LOG.info("{} Connected".format(self.__log_prefix))
            LOG.exception(self._log_prefix + str(ex))

    def upload(self, firmware):
        # No upload provided method for this Port
        return False

    #endregion

    # region UART BLE ARANCINO PORT METADATA

    # endregion
