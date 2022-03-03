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

from arancino.transmitter.sender.Sender import Sender
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
import paho.mqtt.client as mqtt
import time


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class SenderMqtt(Sender):

    def __init__(self, cfg=None):
        super().__init__(cfg=cfg)

        #private
        self.__use_tls = self.cfg["sender.mqtt"]["use_tls"]  #CONF.get_transmitter_sender_mqtt_use_tls()
        self.__qos = self.cfg["sender.mqtt"]["qos"] #CONF.get_transmitter_sender_mqtt_qos()
        self.__retain = self.cfg["sender.mqtt"]["retain"] #CONF.get_transmitter_sender_mqtt_retain()
        self.__broker_host = self.cfg["sender.mqtt"]["host"] #CONF.get_transmitter_sender_mqtt_host()
        self.__broker_port = self.cfg["sender.mqtt"]["port"] #CONF.get_transmitter_sender_mqtt_port()

        self.__client = None

        if self.__use_tls:
            self.__ca_file = self.cfg["sender.mqtt"]["ca_file"] #CONF.get_transmitter_sender_mqtt_ca_path()
            self.__cert_file = self.cfg["sender.mqtt"]["cert_file"] #CONF.get_transmitter_sender_mqtt_cert_path()
            self.__key_file = self.cfg["sender.mqtt"]["key_file"] #CONF.get_transmitter_sender_mqtt_key_path()
        else:
            self.__username = self.cfg["sender.mqtt"]["username"] #CONF.get_transmitter_sender_mqtt_username()
            self.__password = self.cfg["sender.mqtt"]["password"] #CONF.get_transmitter_sender_mqtt_password()
        
        #protected
        self._topic = self.cfg["sender.mqtt"]["topic"]  # CONF.get_transmitter_sender_mqtt_topic()

        self._log_prefix = "Sender [Mqtt] - "



    def start(self):
        self.__client = self.__get_connection()


    def stop(self):
        if self.__client and self.__client.connected_flag:
            self.__client.loop_stop()
            self.__client.disconnect()

    def _do_trasmission(self, data=None, metadata=None):
        if self.__client and self.__client.connected_flag:

            LOG.debug("{}Sending data to {}:{}...".format(self._log_prefix, self.__broker_host, str(self.__broker_port)))
            info = self.__client.publish(topic=self._topic, payload=data, qos=self.__qos, retain=self.__retain)

            if info.rc == mqtt.MQTT_ERR_SUCCESS:
                LOG.info("{}Data sent to {}:{}".format(self._log_prefix, self.__broker_host, str(self.__broker_port)))
                return True
            else:
                LOG.warning("{}Warning while sending data to {}:{} - {}".format(self._log_prefix, self.__broker_host, str(self.__broker_port), mqtt.error_string(info.rc)))
                return False

        else:
            LOG.warning("{}Can not send data to {}:{}".format(self._log_prefix, self.__broker_host, str(self.__broker_port)))
            return False


    def __get_connection(self):

        LOG.debug("{}Connecting to {}:{}...".format(self._log_prefix, self.__broker_host, str(self.__broker_port)))
        client = None

        try:
            client = mqtt.Client()
            client.connected_flag = False
            if self.__use_tls:
                client.tls_set(ca_certs=self.__ca_file, certfile=self.__cert_file, keyfile=self.__key_file)
            else:
                client.username_pw_set(username=self.__username, password=self.__password)

            client.on_connect = self.__on_connect
            client.on_disconnect = self.__on_disconnect
            client.connect(self.__broker_host, self.__broker_port, 60)
            client.loop_start()

        except Exception as ex:

            del client
            client = None
            LOG.error("{}Error during connecting to {}:{}: {}".format(self._log_prefix, str(ex), self.__broker_host, str(self.__broker_port)), exc_info=TRACE)

        finally:
            return client

    # region Connect Handler
    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.__client.connected_flag = True
            LOG.info("{}Connected to {}:{}...".format(self._log_prefix, self.__broker_host, str(self.__broker_port)))
        else:
            self.__client.connected_flag = False
            LOG.warning("{}Failed to connect to {}:{} - {}".format(self._log_prefix, self.__broker_host,str(self.__broker_port), mqtt.connack_string(rc)))
    # endregion

    # region Disconnect Handler
    def __on_disconnect(self, client, userdata, rc):
        self.__client.connected_flag = False
        LOG.info("{}Disconnected from {}:{}...".format(self._log_prefix, self.__broker_host, str(self.__broker_port)))
        while rc != 0:
            time.sleep(5)
            LOG.info("Reconnecting to mqtt broker...")
            try:
                rc=self.__client.connect(self.__broker_host, self.__broker_port, 60)
            except Exception as e:
                LOG.error(e)
    # endregion