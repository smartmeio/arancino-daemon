# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 smartme.IO

Authors:  Sergio Tomasello <sergio@smartme.io>
Contributors: Andrea Centorrino <andrea.centorrino@smartme.io>

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



from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.port.mqtt.ArancinoMqttHandler import ArancinoMqttHandler
from arancino.ArancinoCortex import *
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
import time, datetime
import paho.mqtt.client as mqtt 


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()


class ArancinoMqttPort(ArancinoPort):

    def __init__(self, port_id=None, device=None, mqtt_client=None, m_s_plugged=False, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None, timeout=None):

        super().__init__(device=device, port_type=PortTypes.MQTT, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, upload_cmd=None, receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        # SERIAL PORT PARAMETER
        self.__mqtt_client = mqtt_client
        self.__mqtt_topic_cmd_from_mcu = "arancino/cortex/{}/cmd_from_mcu".format(port_id)
        self.__mqtt_topic_rsp_to_mcu = "arancino/cortex/{}/cmd_to_mcu".format(port_id)

        # Command Executor
        self._executor = ArancinoCommandExecutor(port_id=self._id, port_device=self._device, port_type=self._port_type)

        # Misc
        self._compatibility_array = COMPATIBILITY_MATRIX_MOD_MQTT[str(CONF.get_metadata_version().truncate())]
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
        #self.__serial_port.close()

        del self.__mqtt_handler
        #del self.__serial_port

        LOG.warning("{} Mqtt Port closed.".format(self._log_prefix))

        
        # check if the disconnection handler callback function is defined
        if self._disconnection_handler is not None:
            self._disconnection_handler(self._id)
        else:  # do nothing
            pass



    def sendResponse(self, raw_response):
        """
        Send a Response to the mcu. A Response is bind to a Command. The Response is sent only if the Port is Connected.

        :param raw_response: {String} The Response to send back to the MCU.
        :return: void
        """

        if self._m_s_connected:

            ret = self.publish(self.__mqtt_topic_rsp_to_mcu, raw_response, 0)

        else:  # not connected
            LOG.warning("{} Cannot Sent a Response: Port is not connected.".format(self._log_prefix))


    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self._m_c_enabled:
                if not self._m_s_connected:
                    try:
                        LOG.info("{} Connecting...".format(self._log_prefix))
    
                        if CONF.get_port_mqtt_reset_on_connect():
                            # first resetting
                            self.reset()
                        
                        self.__mqtt_handler = ArancinoMqttHandler("ArancinoMqttHandler-"+self._id, self.__mqtt_client, self._id, self._device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
                        self._m_s_connected = True
                        
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
                
                self.__mqtt_handler.stop()

            else:
                LOG.debug("{} Already Disconnected".format(self._log_prefix))


        except Exception as ex:
            raise ex

def reset(self):
        """

        :return:
        """
        LOG.warning("{} Cannot Reset".format(self._log_prefix))

def upload(self):
        """

        :return:
        """
        LOG.warning("{} Cannot Upload".format(self._log_prefix))