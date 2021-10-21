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



from arancino.utils.ArancinoUtils import ArancinoConfig
from arancino.port.ArancinoPortFilter import FilterTypes
from arancino.port.mqtt.ArancinoMqttPortFilter import ArancinoMqttPortFilter
from arancino.port.mqtt.ArancinoMqttPort import ArancinoMqttPort
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe

CONF = ArancinoConfig.Instance()

class ArancinoMqttDiscovery(object):

    def __init__(self):
        self.__filter = ArancinoMqttPortFilter()
        self.__filter_type = "ALL"#CONF.get_port_serial_filter_type()
        self.__filter_list = []#CONF.get_port_serial_filter_list()

        self.__list_discovered = []

        # TODO prendere da configurazione
        self.__mqtt_discovery_topic = "arancino/discovery"
        self.__mqtt_arancino_daemon_discovery_user = "arancino-daemon"
        self.__mqtt_arancino_daemon_discovery_pass = "d43mon"
        self.__mqtt_arancino_daemon_broker_host = "server.smartme.io"
        self.__mqtt_arancino_daemon_broker_port = 1883
        
        # TODO gestire eccezioni
        self.__mqtt_client = mqtt.Client()
        self.__mqtt_client.on_connect = self.__on_connect
        self.__mqtt_client.on_message = self.__on_discovery
        self.__mqtt_client.username_pw_set(self.__mqtt_arancino_daemon_discovery_user, self.__mqtt_arancino_daemon_discovery_pass)
        self.__mqtt_client.connect(self.__mqtt_arancino_daemon_broker_host, self.__mqtt_arancino_daemon_broker_port)
        self.__mqtt_client.loop_start()
    
    def __on_connect(self, client, userdata, flags, rc):  # The callback for when the client connects to the broker

        # TODO LOGga qualcosa

        # client.message_callback_add("arancino_mqtt_port_id_1_cmd/1", self.on_discovery)
        # client.message_callback_add("arancino_mqtt_port_id_1_cmd/2", self.on_message_2)
        client.subscribe("arancino/discovery")
        client.subscribe("arancino/cortex/+/cmd_from_mcu") #
        client.subscribe("arancino/cortex/+/rsp_to_mcu") #


    def __on_discovery(self, client, userdata, msg):
        
        pid = str(msg.payload.decode('utf-8', errors='strict'))
        if pid not in self.__list_discovered:
            self.__list_discovered.append(pid)

        #print("Device Discovered -> " + msg.topic + " " + str(msg.payload))

    # def on_message_2(self, client, userdata, msg):
    #     print("Message 2 received -> " + msg.topic + " " + str(msg.payload))

    def getAvailablePorts(self, collection):
        ports = self.__list_discovered
        ports = self.__preFilterPorts(ports)
        ports = self.__transformInArancinoPorts(ports)
        ports = self.__postFilterPorts(ports=ports, filter_type=self.__filter_type, filter_list=self.__filter_list)

        return ports


    def __preFilterPorts(self, ports):
        """
        Pre Filter Mqtt Ports
        :param ports: List of ID
        :return ports_filterd: List
        """
        #ports_filterd = []

        # for port in ports:
        #     if port.serial_number != None and port.serial_number != "FFFFFFFFFFFFFFFFFFFF" and port.vid != None and port.pid != None:
        #         ports_filterd.append(port)

        return ports


    def __postFilterPorts(self, ports={}, filter_type=FilterTypes.ALL, filter_list=[]):

        if filter_type == FilterTypes.ONLY:
            return self.__filter.filterOnly(ports, filter_list)

        elif filter_type == FilterTypes.EXCLUDE:
            return self.__filter.filterExclude(ports, filter_list)

        elif filter_type == FilterTypes.ALL:
            return self.__filter.filterAll(ports, filter_list)




    def __transformInArancinoPorts(self, ports):
        """
        This methods creates a new structure starting from a List of ID 
        rapresenting Port connected via MQTT.


        :param ports: List of ID rapresenting Port connected via MQTT.
        :return: Dict of ArancinoPorts with additional information
        """
        new_ports_struct = {}

        for port in ports:

            p = ArancinoMqttPort(   port_id = port, #port is the id of the port sent via MQTT into discovery topic
                                    device = None,
                                    mqtt_client = self.__mqtt_client,
                                    m_s_plugged=True, 
                                    m_c_enabled=CONF.get_port_serial_enabled(), 
                                    m_c_hide=CONF.get_port_serial_hide() )
            
            new_ports_struct[p.getId()] = p

        return new_ports_struct