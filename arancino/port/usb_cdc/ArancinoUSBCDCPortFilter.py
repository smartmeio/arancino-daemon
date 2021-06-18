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

from arancino.port.ArancinoPortFilter import ArancinoPortFilter

class ArancinoUSBCDCPortFilter(ArancinoPortFilter):


    def __init__(self):
        pass


    def filterAll(self, ports={}, list=[]):
        return ports


    def filterExclude(self, ports={}, list=[]):

        filtered_ports = {}

        for id, port in ports.items():
            item = (port.getVID() + ":" + port.getPID()).upper()
            if item not in list:
                filtered_ports[id] = port

        return filtered_ports


    def filterOnly(self, ports={}, list=[]):

        filtered_ports = {}

        for id, port in ports.items():
            item = (port.getVID() + ":" + port.getPID()).upper()
            if item in list:
                filtered_ports[id] = port

        return filtered_ports
