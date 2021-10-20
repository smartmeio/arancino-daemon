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

CONF = ArancinoConfig.Instance()

class ArancinoMqttDiscovery:

    def __init__(self):
        self.__filter = ArancinoMqttPortFilter()
        self.__filter_type = "ALL"#CONF.get_port_serial_filter_type()
        self.__filter_list = []#CONF.get_port_serial_filter_list()

        self.__mqtt_connection = None
        self.__mqtt_discovery_topic = "discovery"
        self.__mqtt_arancino_daemon_discovery_user = "arancino-daemon-discovery"
        self.__mqtt_arancino_daemon_discovery_pass = ""
        
        


    def getAvailablePorts(self, collection):
        pass