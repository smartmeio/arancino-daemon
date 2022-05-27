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
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig2, stringToBool
import paho.mqtt.client as mqtt
import time


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig2.Instance().cfg
TRACE = CONF.get('log').get('trace')

class SenderMqtt(Sender):

    def __init__(self, cfg=None):
        super().__init__(cfg=cfg)

        #private
        self._use_tls = self.cfg.get("mqtt").get("use_tls") #CONF.get_transmitter_sender_mqtt_use_tls()
        self._qos = self.cfg.get("mqtt").get("qos") #CONF.get_transmitter_sender_mqtt_qos()
        self._retain = self.cfg.get("mqtt").get("retain") #CONF.get_transmitter_sender_mqtt_retain()
        self._broker_host = self.cfg.get("mqtt").get("host") #CONF.get_transmitter_sender_mqtt_host()
        self._broker_port = self.cfg.get("mqtt").get("port") #CONF.get_transmitter_sender_mqtt_port()

        self._client = None

        if self._use_tls:
            self._ca_file = self.cfg.get("mqtt").get("ca_file") #CONF.get_transmitter_sender_mqtt_ca_path()
            self._cert_file = self.cfg.get("mqtt").get("cert_file") #CONF.get_transmitter_sender_mqtt_cert_path()
            self._key_file = self.cfg.get("mqtt").get("key_file") #CONF.get_transmitter_sender_mqtt_key_path()
        else:
            self._username = self.cfg.get("mqtt").get("username") #CONF.get_transmitter_sender_mqtt_username()
            self._password = self.cfg.get("mqtt").get("password") #CONF.get_transmitter_sender_mqtt_password()
        
        #protected
        self._topic = self.cfg.get("mqtt").get("topic")  # CONF.get_transmitter_sender_mqtt_topic()



    def start(self):
        self._client = self.__get_connection()


    def stop(self):
        if self._client and self._client.connected_flag:
            self._client.loop_stop()
            self._client.disconnect()

    def _do_trasmission(self, data=None, metadata=None):
        if self._client and self._client.connected_flag and len(data):

            LOG.debug("{}Sending data to {}:{}...".format(self._log_prefix, self._broker_host, str(self._broker_port)))
            info = self._client.publish(topic=self._topic, payload=data, qos=self._qos, retain=self._retain)

            if info.rc == mqtt.MQTT_ERR_SUCCESS:
                LOG.info("{}Data sent to {}:{}".format(self._log_prefix, self._broker_host, str(self._broker_port)))
                return True
            else:
                LOG.warning("{}Warning while sending data to {}:{} - {}".format(self._log_prefix, self._broker_host, str(self._broker_port), mqtt.error_string(info.rc)))
                return False

        else:
            LOG.warning("{}Can not send data to {}:{}".format(self._log_prefix, self._broker_host, str(self._broker_port)))
            return False


    def __get_connection(self):

        LOG.debug("{}Connecting to {}:{}...".format(self._log_prefix, self._broker_host, str(self._broker_port)))
        client = None

        try:
            client = mqtt.Client()
            client.connected_flag = False
            if self._use_tls:
                client.tls_set(ca_certs=self._ca_file, certfile=self._cert_file, keyfile=self._key_file)
            else:
                client.username_pw_set(username=self._username, password=self._password)

            client.on_connect = self.__on_connect
            client.on_disconnect = self.__on_disconnect
            client.connect(self._broker_host, self._broker_port, 60)
            client.loop_start()

        except Exception as ex:

            del client
            client = None
            LOG.error("{}Error during connecting to {}:{}: {}".format(self._log_prefix, str(ex), self._broker_host, str(self._broker_port)), exc_info=TRACE)

        finally:
            return client

    # region Connect Handler
    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._client.connected_flag = True
            LOG.info("{}Connected to {}:{}...".format(self._log_prefix, self._broker_host, str(self._broker_port)))
        else:
            self._client.connected_flag = False
            LOG.warning("{}Failed to connect to {}:{} - {}".format(self._log_prefix, self._broker_host, str(self._broker_port), mqtt.connack_string(rc)))
    # endregion

    # region Disconnect Handler
    def __on_disconnect(self, client, userdata, rc):
        self._client.connected_flag = False
        LOG.info("{}Disconnected from {}:{}...".format(self._log_prefix, self._broker_host, str(self._broker_port)))
        while rc != 0:
            time.sleep(5)
            LOG.info("Reconnecting to mqtt broker...")
            try:
                rc = self._client.connect(self._broker_host, self._broker_port, 60)
            except Exception as e:
                LOG.error(e)
    # endregion