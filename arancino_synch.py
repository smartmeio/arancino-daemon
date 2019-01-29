'''
SPDX-license-identifier: Apache-2.0

Copyright (C) 2019 SmartMe.IO

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
'''

from arancino_datastore import ArancinoDataStore
import arancino_constants as const


class ArancinoSynch:

    def __init__(self):
        self.__ds = ArancinoDataStore()
        self.__datastore = self.__ds.getDataStore()
        self.__devicestore = self.__ds.getDeviceStore()

    def synchPorts(self, ports):
        """
        :param ports: Dictionary of ArancinoPorts
        """

        for id, arancino in ports.items():
            self.synchPort(arancino)


    def synchPort(self, port):
        """
        Makes a synchronization between the list of plugged ports and the device store
            Some values are to be considered as Status Metadata because the represent the current status of the port,
            others are to be considered as Configuration Metadata because they are setted up by the user.

            Status Metadata are: Plugged, Connected,...

        Comfiguration Metadata are ever synchronized from device store to the in memory data structure (plugged ports),
            meanwhile Status Port are synchronized from data structure to the device store.

            Configuration Metadata are: Enabled, Alias,...

        :param ports: ArancinoPorts
        """

        arancino = port

        if self.__devicestore.exists(arancino.id) == 1:  # the port is already registered in devicestore
            '''
            Configuration Metadata

            The following line of code are executed every time a specific port/device is plugged. 
                It runs only if a port/device is already registerd.

            When a port/device is contained in devicestore, its configuration data are loaded 
                from devicestore and stored into in-memory data structure. The data flow in this 
                synchronization phase is from "Redis" to "In Memory". 

            Uses __checkValues function to automatically cast values before storing into 
                in-memory data structure.

            '''
            arancino.enabled = self.__checkValues(self.__devicestore.hget(arancino.id, const.M_ENABLED), "BOOL")
            arancino.auto_connect = self.__checkValues(self.__devicestore.hget(arancino.id, const.M_AUTO_CONNECT), "BOOL")
            arancino.alias = self.__devicestore.hget(arancino.id, const.M_ALIAS)



        else:
            '''
            The port does not exist in the device store and must be registered. This runs only 
            the first time a port is plugged and all ports data are stored into device store. 
            Boolean and Integer object types and None will be stored as String automatically

            Data are stored using the port id as key in hash of redis, the defined above keys as fields, and values as values
            '''
            self.__devicestore.hset(arancino.id, const.M_ENABLED, arancino.enabled)
            self.__devicestore.hset(arancino.id, const.M_AUTO_CONNECT, arancino.auto_connect)
            self.__devicestore.hset(arancino.id, const.M_ALIAS, arancino.alias)
            self.__devicestore.hset(arancino.id, const.P_NAME, arancino.port.name)
            self.__devicestore.hset(arancino.id, const.P_DESCRIPTION, arancino.port.description)
            self.__devicestore.hset(arancino.id, const.P_HWID, arancino.port.hwid)
            self.__devicestore.hset(arancino.id, const.P_VID, hex(arancino.port.vid))
            self.__devicestore.hset(arancino.id, const.P_PID, hex(arancino.port.pid))
            self.__devicestore.hset(arancino.id, const.P_SERIALNUMBER, arancino.port.serial_number)
            self.__devicestore.hset(arancino.id, const.P_MANUFACTURER, arancino.port.manufacturer)
            self.__devicestore.hset(arancino.id, const.P_PRODUCT, arancino.port.product)

        '''
        Status Metadata

        Updates metadata in the list (from list to redis) every time
        '''
        self.__devicestore.hset(arancino.id, const.M_PLUGGED, arancino.plugged)
        self.__devicestore.hset(arancino.id, const.M_CONNECTED, arancino.connected)
        self.__devicestore.hset(arancino.id, const.P_DEVICE, arancino.port.device)
        self.__devicestore.hset(arancino.id, const.P_LOCATION, arancino.port.location)
        self.__devicestore.hset(arancino.id, const.P_INTERFACE, arancino.port.interface)
        # TODO manage datetime
        # self.devicestore.hset(id, const.M_DATETIME, strftime("%Y-%m-%d %H:%M:%S", localtime()))


    def __checkValues(self, value, type):
        '''
        :param value: String Value to convert
        :param type: Oject Type in which the Value is to be converted
        :return: Converted Object
        '''

        __val = None

        if type.upper() == "BOOL" or type.upper() == "BOOLEAN":
            __val = (value.upper() == "TRUE")
        # TODO datetime
        # TODO put datetime format in configuration file
        #else:
        #    if type.upper() == "DATETIME":
        #        __val = time.strptime(value, "%Y-%m-%d %H:%M:%S")

        return __val
