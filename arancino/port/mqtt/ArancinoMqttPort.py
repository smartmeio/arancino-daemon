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

    def __init__(self, port_info=None, device=None, mqtt_client_name="arancino-daemon", mqtt_client_password="d43mon", mqtt_broker_host="server.smartme.io", mqtt_broker_port=1883, m_s_plugged=False, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None, timeout=None):

        super().__init__(device=device, port_type=PortTypes.MQTT, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, upload_cmd=CONF.get_port_serial_upload_command(), receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        # SERIAL PORT PARAMETER
        self.__mqtt_topic_cmd = "arancino_mqtt_port_id_1_cmd"
        self.__mqtt_topic_rsp = "rsp_port_id_1"
        self.__mqtt_client_name = mqtt_client_name
        self.__mqtt_client_password = mqtt_client_password
        self.__mqtt_broker_host = mqtt_broker_host
        self.__mqtt_broker_port = mqtt_broker_port

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

        """
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
            ##### TODO QUI FARE LA PUBBLISH
            LOG.info("Publishing")
            ret=self.publish("mqtt/python", "test message 0", 0)
            LOG.info("Published return=" + str(ret))
            
            ########self.__serial_port.write(raw_response.encode())
        
        else:  # not connected
            LOG.warning("{} Cannot Sent a Response: Port is not connected.".format(self._log_prefix))


    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self._m_c_enabled:
                if not self._m_s_connected:
                    try:
                        LOG.info("{} Connecting...".format(self._log_prefix))

                        """
                        if CONF.get_port_serial_reset_on_connect():
                            # first resetting
                            self.reset()
                        """


                        ##### TODO QUI FARE LA CONNESSIONE MQTT
                        #mqtt.Client.connected_flag=False
                        username= "arancino-daemon"
                        password="d43mon"
                        broker= "server.smartme.io"
                        port=1883

                        client = mqtt.Client()         #create a new istance
                        client.username_pw_set(username, password)  #Set a username and optionally a password for broker authentication.

                        client.connect(broker,port)
                        
                        
                        #######

                        #self.__serial_handler = ArancinoSerialHandler("ArancinoSerialHandler-"+self._id, self.__serial_port, self._id, self._device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
                        self._m_s_connected = True
                        #self.__serial_handler.start()
                        
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
        """

        :return:
        """
        pass
def reset(self):
        """

        :return:
        """
        pass

def upload(self):
        """

        :return:
        """
        pass