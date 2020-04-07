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

from serial.tools import list_ports as list
import arancino.arancino_conf as conf

# logger
LOG = conf.logger

class ArancinoPortsDiscovery:

    def __init__(self):
        pass

    def getPluggedArancinoPorts(self, prev_plugged, connected):
        """
        Using python-serial library, it scans the serial ports applies filters and then
            returns a Dictionary of ArancinoPort
        :return Dictionary of ArancinoPort
        """

        self.__ports = list.comports()
        self.__ports = self.__filterSerialPorts(self.__ports)
        self.__ports = self.__transformInArancinoPorts(self.__ports, connected)
        return self.__ports

    def __filterSerialPorts(self, ports):
        """
        Filters Serial Ports with valid Serial Number, VID and PID
        :param ports: List of ListPortInfo
        :return ports_filterd: List
        """
        ports_filterd = []
        hwids = conf.hwid
        for port in ports:
            if port.serial_number != None and port.serial_number != "FFFFFFFFFFFFFFFFFFFF" and port.vid != None and port.pid != None:
                if len(hwids) > 0: # apply the filter only if at least one vid:pid is defined in conf file.
                    for hwid in hwids:
                        hwid = hwid.split(":")
                        if hex(port.vid) == hex(int(hwid[0], 16)) and hex(port.pid) == hex(int(hwid[1], 16)):
                            ports_filterd.append(port)
                else: # don't apply the filter
                    ports_filterd.append(port)

        return ports_filterd

    def __transformInArancinoPorts(self, ports, connected):
        """
        This methods creates a new structure starting from a List of ListPortInfo.
        A base element of the new structure is composed by some metadata and
        the initial object of type ListPortInfo


        :param ports: List of plugged port (ListPortInfo)
        :return: Dict of Ports with additional information
        """
        new_ports_struct = {}

        for port in ports:

            p = ArancinoPort(port, plugged=True)

            if p.id in connected:
                p.connected = True

            new_ports_struct[p.id] = p

        return new_ports_struct


    '''
    def __encrypt_string(self, hash_string):
        sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
        return sha_signature
    '''


class ArancinoPort:

    def __init__(self, port, enabled=conf.port['enabled'], auto_connect=conf.port['auto_connect'], alias="", plugged=False, connected=False, hide=conf.port['hide']):
        # serial port
        self.port = port

        # serial port identification
        #self.id = port.serial_number

        # configuration metadata
        self.enabled = enabled
        self.auto_connect = auto_connect
        self.alias = alias
        self.hide = hide

        # status metadata
        self.plugged = plugged
        self.connected = connected

        #todo datetime attribute

    @property
    def port(self):
        return self.__port


    @port.setter
    def port(self, port):
        self.__port = port
        self.__id = port.serial_number


    @property
    def id(self):
        return self.__id


    @property
    def enabled(self):
        return self.__enabled


    @enabled.setter
    def enabled(self, enabled):
        self.__enabled = enabled

    @property
    def auto_connect(self):
        return self.__auto_connect


    @auto_connect.setter
    def auto_connect(self, auto_connect):
        self.__auto_connect = auto_connect


    @property
    def alias(self):
        return self.__alias


    @alias.setter
    def alias(self, alias):
        self.__alias = alias


    @property
    def hide(self):
        return self.__hide


    @hide.setter
    def hide(self, hide):
        self.__hide = hide


    @property
    def plugged(self):
        return self.__plugged


    @plugged.setter
    def plugged(self, plugged):
        self.__plugged = plugged


    @property
    def connected(self):
        return self.__connected


    @connected.setter
    def connected(self, connected):
        self.__connected = connected
