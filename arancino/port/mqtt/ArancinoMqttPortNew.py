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



from arancino.port.ArancinoPort import ArancinoPort, PortTypes
from arancino.port.mqtt.ArancinoMqttHandler import ArancinoMqttHandler
#from arancino.ArancinoCortex import *
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment
#from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
import time, datetime
import paho.mqtt.client as mqtt 
from arancino.port.ArancinoPortNew import ArancinoPort, PortTypes
from arancino.ArancinoConstants import ArancinoApiResponseCode

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("log").get("trace")
ENV = ArancinoEnvironment.Instance()


class ArancinoMqttPort(ArancinoPort):

    def __init__(self, id=None, device=None, mqtt_client=None, enabled=True, auto_connect=True, alias="", hide=False, receivedCommandHandler=None, disconnectionHandler=None, timeout=None):

        super().__init__(id=id, device=device, port_type=PortTypes.MQTT, enabled=enabled, alias=alias, hide=hide, upload_cmd=None, receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        self.__mqtt_client = mqtt_client

        #region MQTT PORT TOPICS
        # Topic used by Arancino Daemon (Left Hemisphere) to receive Cortex Commands from Arancino MQTT Ports (Right Hemisphere)
        self.__mqtt_topic_cmd_from_mcu = "{}/{}/cmd_from_mcu".format(CONF.get("port").get("mqtt").get("connection").get("cortex_topic") + "/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id")), self.id)

        # Topic used by Arancino Daemon (Left Hemisphere) to send back Cortex Responses to Arancino MQTT Ports (Right Hemisphere)
        self.__mqtt_topic_rsp_to_mcu = "{}/{}/rsp_to_mcu".format(CONF.get("port").get("mqtt").get("connection").get("cortex_topic") + "/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id")), self.id)

        # Topic used by Arancino Daemon (Left Hemisphere) to send Cortex Commands to Arancino MQTT Ports (Right Hemisphere)
        self.__mqtt_topic_cmd_to_mcu = "{}/{}/cmd_to_mcu".format(CONF.get("port").get("mqtt").get("connection").get("cortex_topic") + "/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id")), self.id)

        # Topic used by Arancino Daemon (Left Hemisphere) to receive back Cortex Responses from Arancino MQTT Ports (Right Hemisphere)
        self.__mqtt_topic_rsp_from_mcu = "{}/{}/rsp_from_mcu".format(CONF.get("port").get("mqtt").get("connection").get("cortex_topic") + "/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id")), self.id)

        # Connection Status: Topic used by Arancino Daemon to manage last will of the MQTT Port
        self.__mqtt_topic_conn_status = "{}/{}".format(CONF.get("port").get("mqtt").get("connection").get("service_topic") + "/connection_status/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id")), self.id)

        # Service Topic: Generic Service Topic
        self.__mqtt_service_topic = "{}/{}/{}".format(CONF.get("port").get("mqtt").get("connection").get("service_topic"), str(CONF.get("port").get("mqtt").get("connection").get("client_id")), self.id)

        #endregion

        # Misc
        self._log_prefix = "[{} - ({}) {} at {}]".format(PortTypes(self.type).name, self.alias, self.id, self.device)

    #region HANDLERS
    def __connectionLostHandler(self):
        """
        This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """

        if not self.isDisconnected():
            self.disconnect()

        LOG.warning("{} Mqtt Port closed.".format(self._log_prefix))

        
        # check if the disconnection handler callback function is defined
        if self._disconnection_handler is not None:
            self._disconnection_handler(self._id)
        else:  # do nothing
            pass

    #endregion


    # region STATES and TRANSITIONS CALLBACKS

    def before_plug(self):
        LOG.debug("{} Before Plug: {}...".format(self._log_prefix, self.state.upper()))


    def on_enter_state_plugged(self):
        LOG.debug("{} Entering State: {}...".format(self._log_prefix, self.state.upper()))


    def on_exit_state_plugged(self):
        LOG.debug("{} Exiting State: {}...".format(self._log_prefix, self.state.upper()))


    def after_plug(self):
        LOG.debug("{} After Plug: {}...".format(self._log_prefix, self.state.upper()))


    def before_connect(self):
        LOG.debug("{} Before Connect: {}...".format(self._log_prefix, self.state.upper()))
        try:
            # check if the device is enabled and not already connected
            if self.isEnabled():
                # if not self.isConnected():
                try:
                    LOG.info("{} Connecting...".format(self._log_prefix))

                    # if CONF.get_port_mqtt_reset_on_connect():
                    # this must be setted to False. If True can be caused an infinite loop of connection and disconnection
                    #    self.reset()

                    self._handler = ArancinoMqttHandler("ArancinoMqttHandler-" + self._id, self.__mqtt_client,
                                                        self._id, self.__mqtt_topic_cmd_from_mcu,
                                                        self.__mqtt_topic_conn_status, self._device,
                                                        self._commandReceivedHandlerAbs,
                                                        self.__connectionLostHandler)

                    LOG.info("{} Connected".format(self._log_prefix))
                    self._start_thread_time = time.time()

                except Exception as ex:
                    # TODO LOG SOMETHING OR NOT?
                    LOG.error("{} Error while connecting: {}".format(self._log_prefix, str(ex)), exc_info=TRACE)
                    raise ex

            # else:
            # TODO LOG or EXCPETION
            #    LOG.warning("{} Port already connected".format(self._log_prefix))

            else:  # not enabled
                # TODO LOG or EXCEPTION
                LOG.warning("{} Port not enabled".format(self._log_prefix))

        except Exception as ex:
            raise ex


    def on_enter_state_connected(self):

        LOG.debug("{} Entering State: {}...".format(self._log_prefix, self.state.upper()))


    def on_exit_state_connected(self):
        LOG.debug("{} Exiting State: {}...".format(self._log_prefix, self.state.upper()))


    def after_connect(self):
        LOG.debug("{} After Connect: {}...".format(self._log_prefix, self.state.upper()))


    def before_start(self):
        LOG.debug("{} Before Start: {}...".format(self._log_prefix, self.state.upper()))


    def on_enter_state_started(self):
        LOG.debug("{} Entering State: {}...".format(self._log_prefix, self.state.upper()))


    def on_exit_state_started(self):
        LOG.debug("{} Exiting State: {}...".format(self._log_prefix, self.state.upper()))


    def after_start(self):
        LOG.debug("{} After Start: {}...".format(self._log_prefix, self.state.upper()))


    def before_disconnect(self):
        LOG.debug("{} Before Disconnect: {}...".format(self._log_prefix, self.state.upper()))

        try:
            # check if the device is already
            # if self.isConnected() or self.isStarted():

            # self.__mqtt_handler.stop()
            self.__mqtt_client.message_callback_remove(self.__mqtt_topic_cmd_from_mcu)
            self.__mqtt_client.message_callback_remove(self.__mqtt_topic_rsp_to_mcu)
            self.__mqtt_client.message_callback_remove(self.__mqtt_topic_cmd_to_mcu)
            self.__mqtt_client.message_callback_remove(self.__mqtt_topic_rsp_from_mcu)
            self.__mqtt_client.message_callback_remove(self.__mqtt_topic_conn_status)
            del self._handler
            self.stopHeartbeat()

            # else:
            # LOG.debug("{} Already Disconnected".format(self._log_prefix))


        except Exception as ex:
            raise ex


    def on_enter_state_disconnected(self):
        LOG.debug("{} Entering State: {}...".format(self._log_prefix, self.state.upper()))


    def on_exit_state_disconnected(self):
        LOG.debug("{} Exiting State: {}...".format(self._log_prefix, self.state.upper()))


    def after_disconnect(self):
        LOG.debug("{} After Disconnect: {}...".format(self._log_prefix, self.state.upper()))

    #endregion


    #region OPERATIONS

    def sendResponse(self, raw_response):
        """
        Send a Response to the mcu. A Response is bind to a Command. The Response is sent only if the Port is Started.

        :param raw_response: {String} The Response to send back to the MCU.
        :return: void
        """

        if self.isStarted():

            ret = self.__mqtt_client.publish(self.__mqtt_topic_rsp_to_mcu, raw_response, 2)
            return True

        else:  # not connected
            LOG.warning("{} Cannot Sent a Response: Port is not Started.".format(self._log_prefix))
            return False


    def reset(self):
        """

        :return:
        """

        self.__mqtt_client.publish("{}".format(self.__mqtt_service_topic), "reset", 2)


        #LOG.warning("{} Cannot Reset".format(self._log_prefix))


    def upload(self):
        """

        :return:
        """
        LOG.warning("{} Cannot Upload".format(self._log_prefix))
        raise NotImplemented("Upload Function is not available for port {}[{}]".format(self.getId(), self.getPortType().name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)

    #endregion