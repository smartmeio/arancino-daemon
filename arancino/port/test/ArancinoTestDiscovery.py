# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2020 SmartMe.IO

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
from arancino.port.ArancinoPort import PortTypes
from arancino.utils.ArancinoUtils import ArancinoConfig
# from arancino.filter import FilterTypes

from arancino.port.test.ArancinoTestPortNew import ArancinoTestPort

CONF = ArancinoConfig.Instance().cfg

class ArancinoTestDiscovery:

    def __init__(self):
        # self.__filter = ArancinoSerialPortFilter()
        # self.__filter_type = CONF.get_port_serial_filter_type()
        # self.__filter_list = CONF.get_port_serial_filter_list()
        self.__portType = PortTypes.TEST

        self.__log_prefix = "Arancino Discovery {}".format(self.__portType.name)


    # TODO: this can be an abstract method
    def getAvailablePorts(self, collection):
        """
        Create Arancino Port for test purpose.
            It simulates a disovery service and create a number of Test Ports as by setted in the port.test section of arancino.*.cfg.
            Usually this function is called periodically and a list of Test Port is passed as argument.
        """

        #ports = {}
        num = CONF.get("port").get("test").get("num")
        tmpl_id = CONF.get("port").get("test").get("id_template")
        test_ports = []
        for count in range(1, int(num)+1):  # Generates port ids
            id = tmpl_id + str(count)
            test_ports.append(id)

            # if the id is not in passed list of ports, then create a Test Port and put it in the list.
            if id not in collection:

                p_enabled = CONF.get("port").get("test").get("auto_enable")
                p_hide = CONF.get("port").get("test").get("hide")

                port = ArancinoTestPort(id=id, device="There", enabled=p_enabled, auto_connect=True, alias=id, hide=p_hide)
                #ports[id] = port
                collection[id] = port
            else:
                pass #del collection[id]


        # get each port in the collection
        for id in list(collection):  # using list() prevent the `RuntimeError: dictionary changed size during iteration` becouse list() make a copy of the object

            # if a port in the collection is not in the list of the test_port (the created one) means that the port was unplegged.
            if id not in test_ports:
                del collection[id]


        return collection#ports

    def stop(self):
        pass

    #def __discoveryPorts(self):
