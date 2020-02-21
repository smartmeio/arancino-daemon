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

#from arancino.arancino_datastore import ArancinoDataStore
#import arancino.arancino_constants as const

from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.ArancinoConstants import ArancinoDBKeys

class ArancinoPortSynch:


    def __init__(self):
        #self.__ds = ads  # ArancinoDataStore()
        self.__datastore = ArancinoDataStore.Instance().getDataStore()
        self.__devicestore = ArancinoDataStore.Instance().getDeviceStore()


    def synchPorts(self, ports):
        """
        :param ports: Dictionary of ArancinoPorts
        """

        for id, arancino_port in ports.items():
            self.__synchPort(arancino_port)

        self.__synchClean(ports)


    def __synchPort(self, arancino_port):
        """
        Makes a synchronization between the list of plugged ports and the device store
            Some values are to be considered as Status Metadata because they represent the current status of the port,
            others are to be considered as Configuration Metadata because they are setted up by the user.

            Status Metadata are: Plugged, Connected,...

        Comfiguration Metadata are ever synchronized from device store to the in memory data structure (plugged ports),
            meanwhile Status Metadata are synchronized from data structure to the device store.

            Configuration Metadata are: Enabled, Alias,...

        :param ports: ArancinoPorts
        """

        arancino = arancino_port

        if self.__devicestore.exists(arancino.getId()) == 1:  # the port is already registered in the device store
            '''
            Configuration Metadata

            The following line of code are executed every time a specific port/device is plugged. 
                It runs only if a port/device is already registerd.

            When a port/device is contained in the device store, its configuration data are loaded 
                from devicestore and stored into in-memory data structure. The data flow in this 
                synchronization phase is from "Redis" to "In Memory". 

            Uses __checkValues function to automatically cast values before storing into 
                in-memory data structure.

            '''
            enabled = self.__checkValues(self.__devicestore.hget(arancino.getId(), ArancinoDBKeys.M_ENABLED), "BOOL")
            auto_connect = self.__checkValues(self.__devicestore.hget(arancino.getId(), ArancinoDBKeys.M_AUTO_CONNECT), "BOOL")
            alias = self.__devicestore.hget(arancino.getId(), ArancinoDBKeys.M_ALIAS)

            arancino.setEnabled(enabled)
            arancino.setAutoConnect(auto_connect)
            arancino.setAlias(alias)



        else:
            '''
            The port does not exist in the device store and must be registered. This runs only 
            the first time a port is plugged and all ports data are stored into device store. 
            Boolean and Integer object types and None will be stored as String automatically

            Data are stored using the port id as Redis Key in Redis Hash, the defined above keys as Redis Fields, and values as Redis Values

            Eg:

            | Key - Port Id                     | Metadata Key - Field      | Metadata Value - Value |
            |-----------------------------------|---------------------------|------------------------|
            | 1ABDF7C5504E4B53382E314AFF0C1B2D  | M_ENABLED                 | True                   |
            | 1ABDF7C5504E4B53382E314AFF0C1B2D  | P_DEVICE                  | /dev/tty.ACM0          |


            '''
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.M_ENABLED, str(arancino.isEnabled()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.M_AUTO_CONNECT, str(arancino.getAutoConnect()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.M_ALIAS, str(arancino.getAlias()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_DESCRIPTION, str(arancino.getDescription()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_HWID, str(arancino.getHWID()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_VID, str(arancino.getVID()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_PID, str(arancino.getPID()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_SERIALNUMBER, str(arancino.getSerialNumber()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_MANUFACTURER, str(arancino.getManufacturer()))
            self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_PRODUCT, str(arancino.getProduct()))

        '''
        Status Metadata

        Updates metadata in the list (from list to redis) every time
        '''
        self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.M_PLUGGED, str(arancino.isPlugged()))
        self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.M_CONNECTED, str(arancino.isConnected()))
        self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_DEVICE, str(arancino.getDevice()))
        self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_LOCATION, str(arancino.getLocation()))
        self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_INTERFACE, str(arancino.getInterface()))
        self.__devicestore.hset(arancino.getId(), ArancinoDBKeys.P_NAME, str(arancino.getName()))
        # TODO manage datetime
        # self.devicestore.hset(id, const.M_DATETIME, strftime("%Y-%m-%d %H:%M:%S", localtime()))


    def __synchClean(self, ports):
        """
        :param ports: Dictionary of ArancinoPorts
        """
        keys = self.__devicestore.keys()

        # if there are registered ports in devicestore
        if len(keys) > 0:

            diff = {}
            items = {}

            if ports is not None:
                items = ports

            diff = set(keys).difference(items)

            for it in diff:
                self.__devicestore.hset(it, ArancinoDBKeys.M_PLUGGED, str(False))
                self.__devicestore.hset(it, ArancinoDBKeys.M_CONNECTED, str(False))
                self.__devicestore.hset(it, ArancinoDBKeys.P_INTERFACE, "")
                self.__devicestore.hset(it, ArancinoDBKeys.P_LOCATION, "")
                self.__devicestore.hset(it, ArancinoDBKeys.P_LOCATION, "")


    def __checkValues(self, value, type):
        '''
        :param value: String Value to convert
        :param type: Oject Type in which the Value is to be converted
        :return: Converted Object
        '''

        __val = None

        if type.upper() == "BOOL" or type.upper() == "BOOLEAN":
            if value is not None:
                __val = (value.upper() == "TRUE")
            else:
                __val = False
        # TODO datetime
        # TODO put datetime format in configuration file
        # else:
        #    if type.upper() == "DATETIME":
        #        __val = time.strptime(value, "%Y-%m-%d %H:%M:%S")

        return __val
