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



from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment
from arancino.port.ArancinoPortFilter import FilterTypes
from arancino.port.mqtt.ArancinoMqttPortFilter import ArancinoMqttPortFilter
from arancino.port.mqtt.ArancinoMqttPort import ArancinoMqttPort
from arancino.port.ArancinoPort import PortTypes
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import time

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
ENV = ArancinoEnvironment.Instance()
TRACE = CONF.get("log").get("trace")

class ArancinoMqttDiscovery(object):

    def __init__(self):
        self.__filter = ArancinoMqttPortFilter()
        self.__filter_type = CONF.get("port").get("mqtt").get("filter_type")
        self.__filter_list = CONF.get("port").get("mqtt").get("filter_list")

        self.__list_discovered = []
        self.__list_discovered_handy = []
        self._log_prefix = "[{} Discovery]".format(PortTypes.MQTT.name)

        self.__mqtt_discovery_topic = CONF.get("port").get("mqtt").get("connection").get("discovery_topic") + "/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id"))
        self.__mqtt_cortex_topic = CONF.get("port").get("mqtt").get("connection").get("cortex_topic") + "/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id"))
        self.__mqtt_service_topic = CONF.get("port").get("mqtt").get("connection").get("service_topic") + "/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id"))
        self.__mqtt_conn_status_topic = CONF.get("port").get("mqtt").get("connection").get("service_topic") + "/connection_status/" + str(CONF.get("port").get("mqtt").get("connection").get("client_id"))
        self.__mqtt_arancino_daemon_discovery_user = str(CONF.get("port").get("mqtt").get("connection").get("username"))
        self.__mqtt_arancino_daemon_discovery_pass = str(CONF.get("port").get("mqtt").get("connection").get("password"))
        self.__mqtt_arancino_daemon_broker_host = str(CONF.get("port").get("mqtt").get("connection").get("host"))
        self.__mqtt_arancino_daemon_broker_port = CONF.get("port").get("mqtt").get("connection").get("port")
        self.__mqtt_arancino_daemon_client_id = str(CONF.get("port").get("mqtt").get("connection").get("client_id"))
        self.__mqtt_arancino_daemon_tls_set = CONF.get("port").get("mqtt").get("connection").get("use_tls")
        self.__mqtt_arancino_daemon_ca_certs = CONF.get("port").get("mqtt").get("connection").get("ca_path")
        self.__mqtt_arancino_daemon_certfile = CONF.get("port").get("mqtt").get("connection").get("cert_path")
        self.__mqtt_arancino_daemon_keyfile = CONF.get("port").get("mqtt").get("connection").get("key_path")
        self.__mqtt_arancino_reset_on_connect = CONF.get("port").get("mqtt").get("connection").get("reset_on_connect")

        
        try:
            self.__mqtt_client = mqtt.Client(client_id="{}-{}".format(self.__mqtt_arancino_daemon_client_id, ENV.serial_number))
            self.__mqtt_client.on_connect = self.__on_connect
            self.__mqtt_client.on_disconnect = self.__on_disconnect
            #self.__mqtt_client.on_message = self.__on_discovery

            self.__mqtt_client.username_pw_set(self.__mqtt_arancino_daemon_discovery_user, self.__mqtt_arancino_daemon_discovery_pass)
            
            if (self.__mqtt_arancino_daemon_tls_set):
                self.__mqtt_client.tls_set(
                    ca_certs=self.__mqtt_arancino_daemon_ca_certs,
                    certfile=self.__mqtt_arancino_daemon_certfile,
                    keyfile=self.__mqtt_arancino_daemon_keyfile
                )

            self.__mqtt_client.connect(self.__mqtt_arancino_daemon_broker_host, self.__mqtt_arancino_daemon_broker_port)
            self.__mqtt_client.loop_start()
        
        except Exception as ex:
            LOG.error("{}Error during connecting to {}:{}: {}".format(self._log_prefix, str(ex), self.__mqtt_arancino_daemon_broker_host, str(self.__mqtt_arancino_daemon_broker_port)), exc_info=TRACE)
    
    # region MQTT Client Handler
    # region ON CONNECT
    def __on_connect(self, client, userdata, flags, rc):  # The callback for when the client connects to the broker

        if rc == 0:
            #self.__client.connected_flag = True
            LOG.debug("{} Connected to {}:{}...".format(self._log_prefix, self.__mqtt_arancino_daemon_broker_host, str(self.__mqtt_arancino_daemon_broker_port)))

            client.subscribe(self.__mqtt_discovery_topic, qos=2)
            client.message_callback_add(self.__mqtt_discovery_topic, self.__on_discovery)

            #client.subscribe("{}/+/{}/cmd_from_mcu".format(self.__mqtt_cortex_topic, pid))   # used to send response to the mqtt port
            #client.subscribe(self.__mqtt_discovery_topic + "/+/rsp_from_mcu")   # for future use: when the daemon will send cmd to the port, it will response in this topic

            if self.__mqtt_arancino_reset_on_connect:
                # reset all mcu connected at the broker by sending a special cmd
                client.publish("{}".format(self.__mqtt_service_topic), "reset", 2)

            for pid in self.__list_discovered:
                #client.subscribe("{}/{}/cmd_from_mcu".format(self.__mqtt_cortex_topic, pid), qos=2)  # used to send response to the mqtt port
                self.__topic_subcriptions(client, pid)

        else:
            #self.__client.connected_flag = False
            LOG.warning("{}Failed to connect to {}:{} - {}".format(self._log_prefix, self.__mqtt_arancino_daemon_broker_host,str(self.__mqtt_arancino_daemon_broker_port), mqtt.connack_string(rc)))
    # endregion

    # region ON DISCOVERY
    def __on_discovery(self, client, userdata, msg):

        pid = str(msg.payload.decode('utf-8', errors='strict'))
        if pid not in self.__list_discovered:
            self.__list_discovered.append(pid)
            #client.subscribe("{}/{}/cmd_from_mcu".format(self.__mqtt_cortex_topic, pid), qos=2)  # used to send response to the mqtt port
            self.__topic_subcriptions(client, pid)
    # endregion

    # region ON DICONNECT
    def __on_disconnect(self, client, userdata, rc):
        #self.__client.connected_flag = False
        
        LOG.info("{} Disconnected from {}:{}...".format(self._log_prefix, self.__mqtt_arancino_daemon_broker_host, str(self.__mqtt_arancino_daemon_broker_port)))
        
        while rc != 0:
            
            time.sleep(5)
            LOG.debug("Reconnecting to mqtt broker...")
            
            try:    
                rc = client.connect(self.__mqtt_arancino_daemon_broker_host, self.__mqtt_arancino_daemon_broker_port, 60)

            except Exception as ex:
                LOG.error("{}Error during re-connecting to {}:{}: {}".format(self._log_prefix, str(ex), self.__mqtt_arancino_daemon_broker_host, str(self.__mqtt_arancino_daemon_broker_port)), exc_info=TRACE)
    # endregion

    #region SUBSCRIPTION

    def __topic_subcriptions(self, client, pid):

        # used to send response to the mqtt port
        client.subscribe("{}/{}/cmd_from_mcu".format(self.__mqtt_cortex_topic, pid), qos=2)
        client.subscribe("{}/{}/".format(self.__mqtt_conn_status_topic, pid), qos=2)
        return None

    #endregion

    # endregion


    # def __intersezione(self, arancino_discovered):
        
    #     #  
    #     new_list_discovered = self.__list_discovered.inteserction(arancino_discovered)
    #     return new_list_discovered
        

    def remove_port(self, port):
        self.__list_discovered.remove(port.getId())
        


    def getAvailablePorts(self, collection):
        #if self.__mqtt_client.is_connected:

        #self.__list_discovered =  self.__list_discovered.inteserction(collection)
        #self.__list_discovered = list(set(self.__list_discovered) & set(collection))


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
        return ports


    def __postFilterPorts(self, ports={}, filter_type=FilterTypes.ALL, filter_list=[]):

        if filter_type == FilterTypes.ONLY.name:
            return self.__filter.filterOnly(ports, filter_list)

        elif filter_type == FilterTypes.EXCLUDE.name:
            return self.__filter.filterExclude(ports, filter_list)

        elif filter_type == FilterTypes.ALL.name:
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
                                    device = CONF.get("port").get("mqtt").get("connection").get("host"),
                                    mqtt_client = self.__mqtt_client,
                                    m_s_plugged=True, 
                                    m_c_enabled=CONF.get("port").get("mqtt").get("auto_enable"), 
                                    m_c_hide=CONF.get("port").get("mqtt").get("hide") )
            
            new_ports_struct[p.getId()] = p

        return new_ports_struct