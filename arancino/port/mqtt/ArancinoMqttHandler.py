# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 smartme.IO

Authors:    Sergio Tomasello <sergio@smartme.io>
            Davide Currò <davide.curro99@gmail.com>

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

import threading

import msgpack
from arancino.ArancinoConstants import *
from arancino.utils.ArancinoUtils import *
from arancino.port.ArancinoPort import PortTypes
import paho.mqtt.client as mqtt

from arancino.utils.CheckableQueue import CheckableQueue

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("log").get("trace")

class ArancinoMqttHandler():

    def __init__(self, handler_name, mqtt_client, id, mqtt_topic_cmd_from_mcu, mqtt_topic_conn_status, device, commandReceivedHandler, connectionLostHandler):
        self.__queue = CheckableQueue(2)

        self.__mqtt_client = mqtt_client      # the mqtt client port
        self.__name = handler_name          # the name, usually the arancino port id
        self.__id = id
        self.__device = device
        self.__log_prefix = "[{} - {} at {}]".format(PortTypes(PortTypes.MQTT).name, self.__id, self.__device)

        self.__commandReceivedHandler = commandReceivedHandler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connectionLostHandler = connectionLostHandler    # handler to be called when a connection is lost or stopped

        #self.__partial_command = ""
        #self.__partial_bytes_command = bytearray(b'')
        #self.__stop = False
        
        #self.__mqtt_client.message_callback_add(mqtt_topic_cmd_from_mcu, self.__on_cmd_received)

        self.__mqtt_client.message_callback_add(mqtt_topic_cmd_from_mcu, self.__on_cmd_received)
        self.__mqtt_client.message_callback_add(mqtt_topic_conn_status, self.__on_connection_status)



    def __on_cmd_received(self, client, userdata, msg):
        # LOG.info("message received  ",str(msg.payload.decode("utf-8")), "topic",msg.topic," retained ",msg.retain, " dati ", msg.mid)
        # if message.retain==1:
        #     print("This is a retained message")

        if msg.mid in self.__queue: return

        if self.__queue.full(): self.__queue.get()
        self.__queue.put(msg.mid)

        try:

            self.__commandReceivedHandler(msgpack.unpackb(msg.payload))
    
        except Exception as ex:

            LOG.warning("{} Decode Warning while reading data: {}".format(self.__log_prefix, str(ex)))

        #TODO GESTIRE ECCEZIONI


    #region ON CONNECTION STATUS
    '''
    qui gestione in pratica il last will & testament delle porte connesse
    '''

    def __on_connection_status(self, client, userdata, msg):
        if msg.payload.decode('utf-8').upper() == "OFFLINE":
            self.stop()

    #endregion

    def stop(self):
        LOG.warning("{}Connection lost".format(self.__log_prefix))
        if self.__connectionLostHandler is not None:
            self.__connectionLostHandler()