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
from arancino.ArancinoUtils import stringToBool, stringToDatetime
from arancino.port.ArancinoPort import PortTypes


class ArancinoPortSynch:


    def __init__(self):
        self.__devicestore = ArancinoDataStore.Instance().getDeviceStore()


    def synchPorts(self, discovered, connected):
        """
        :param discovered: Dictionary of ArancinoPorts
        """

        for id, port in discovered.items():
            self.__synchPort(port, connected)

        self.__synchClean(discovered)
        #self.__synchConfig(discovered, connected)


    def __synchPort(self, port, connected):
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

        if self.__devicestore.exists(port.getId()) == 1:  # the port is already registered in the device store
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

            if port.getId() in connected:
                port = connected[port.getId()]

            # BASE CONFIGURATION METADATA
            #enabled = self.__checkValues(self.__devicestore.hget(arancino.getId(), ArancinoDBKeys.M_ENABLED), "BOOL")
            enabled = stringToBool(self.__devicestore.hget(port.getId(), ArancinoDBKeys.C_ENABLED))
            alias = self.__devicestore.hget(port.getId(), ArancinoDBKeys.C_ALIAS)
            hide = self.__devicestore.hget(port.getId(), ArancinoDBKeys.C_HIDE_DEVICE)

            port.setEnabled(enabled)
            port.setAlias(alias)
            port.setHide(hide)

            # OTHER Info
            # TODO Creation Date




        else: # Runs only the first time when a new device is plugged.
            '''
            The port does not exist in the device store and must be registered. This runs only 
            the first time a port is plugged and all ports data are stored into device store. 
            Boolean and Integer object types and None will be stored as String automatically

            Data are stored using the port id as Redis Key in Redis Hash, the defined above keys as Redis Fields, and values as Redis Values

            Eg:

            | Key - Port Id                     | Metadata Key - Field      | Metadata Value - Value |
            |-----------------------------------|---------------------------|------------------------|
            | 1ABDF7C5504E4B53382E314AFF0C1B2D  | M_ENABLED                 | True                   |
            | 1ABDF7C5504E4B53382E314AFF0C1B2D  | M_DEVICE                  | /dev/tty.ACM0          |


            '''

            # BASE ARANCINO CONFIGURATION METADATA
            # sets default configuration (from config file arancino.cfg)
            self.__devicestore.hset(port.getId(), ArancinoDBKeys.C_ENABLED, str(port.isEnabled()))
            self.__devicestore.hset(port.getId(), ArancinoDBKeys.C_ALIAS, str(port.getAlias()))
            self.__devicestore.hset(port.getId(), ArancinoDBKeys.C_HIDE_DEVICE, str(port.isHidden()))

            self.__devicestore.hset(port.getId(), ArancinoDBKeys.B_PORT_TYPE, str(port.getPortType()))
            self.__devicestore.hset(port.getId(), ArancinoDBKeys.B_ID, str(port.getId()))


            if port.getPortType() == PortTypes.SERIAL:
                # SERIAL ARANCINO PORT METADATA
                # sets data retrieved directly from the plugged port
                self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_DESCRIPTION, str(port.getDescription()))
                self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_HWID, str(port.getHWID()))
                self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_VID, str(port.getVID()))
                self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_PID, str(port.getPID()))
                self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_SERIALNUMBER, str(port.getSerialNumber()))
                self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_MANUFACTURER, str(port.getManufacturer()))
                self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_PRODUCT, str(port.getProduct()))
                self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_NAME, str(port.getName()))
            elif port.getPortType() == PortTypes.TEST:
                # Do Nothing: Test Port doesn't have metadata
                pass

        '''
        Status Metadata

        Updates metadata in the list (from list to redis) every time becouse they can change
        '''
        # runs every time

        # BASE ARANCINO STATUS METADATA
        self.__devicestore.hset(port.getId(), ArancinoDBKeys.S_PLUGGED, str(port.isPlugged()))
        self.__devicestore.hset(port.getId(), ArancinoDBKeys.S_CONNECTED, str(port.isConnected()))

        # Port Device can changes (tty or ip address)
        self.__devicestore.hset(port.getId(), ArancinoDBKeys.B_DEVICE, str(port.getDevice()))
        # TODO Last Usage Date

        if port.getPortType() == PortTypes.SERIAL:
            # SERIAL ARANCINO PORT METADATA
            self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_DEVICE, str(port.getDevice()))
            self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_LOCATION, str(port.getLocation()))
            self.__devicestore.hset(port.getId(), ArancinoDBKeys.P_INTERFACE, str(port.getInterface()))
        elif port.getPortType() == PortTypes.TEST:
            #Do Nothing
            pass

        # self.devicestore.hset(id, const.M_DATETIME, strftime("%Y-%m-%d %H:%M:%S", localtime()))


    def __synchClean(self, ports):
        """
        Update devicestore
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

            # every unplugged ports
            for it in diff:

                type = self.__devicestore.hget(it, ArancinoDBKeys.B_PORT_TYPE)
                port_type = PortTypes[type]

                if port_type == PortTypes.SERIAL:
                    self.__devicestore.hset(it, ArancinoDBKeys.S_PLUGGED, str(False))
                    self.__devicestore.hset(it, ArancinoDBKeys.S_CONNECTED, str(False))
                    self.__devicestore.hset(it, ArancinoDBKeys.P_INTERFACE, "")
                    self.__devicestore.hset(it, ArancinoDBKeys.P_LOCATION, "")
                elif port_type == PortTypes.TEST:
                    # do nothing
                    pass


    def __synchConfig(self, ports, connected):

        for id, port in ports.items():
            if id in connected:
                pc = connected[id]
                pc.setEnabled(port.isEnabled())
                pc.setAlias(port.getAlias())
                pc.setHide(port.isHidden())



'''
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
 
print("now =", now)

# dd/mm/YY H:M:S
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("date and time =", dt_string)	


'''


# from timestampt to datetime
'''
from datetime import datetime

timestamp = 1545730073
dt_object = datetime.fromtimestamp(timestamp)

print("dt_object =", dt_object)
print("type(dt_object) =", type(dt_object))

'''

# from datetime to timestamp
'''
from datetime import datetime

# current date and time
now = datetime.now()

timestamp = datetime.timestamp(now)
print("timestamp =", timestamp)


'''