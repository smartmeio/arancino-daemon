'''

Copyright ® SmartMe.IO  2018

LICENSE HERE

Filename:  arancino_port.py
Author: Sergio Tomasello - sergio@smartme.io
Date: 2019 01 14

'''

from serial.tools import list_ports as list


class ArancinoPortsDiscovery:

    def __init__(self):
        pass

    def getPluggedArancinoPorts(self):
        """
        Using python-serial library, it scans the serial ports applies filters and then
            returns a Dictionary of ArancinoPort
        :return Dictionary of ArancinoPort
        """

        #sets the vendor and product ID to check when poll
        #TODO probably change the discovery method instead of pid e vid
        #self.vid = '2a03'
        #self.pid = '804F'
        #self.match = self.vid + ':' + self.pid

        self.__ports = list.comports()
        self.__ports = self.__filterSerialPorts(self.__ports)
        self.__ports = self.__transformInArancinoPorts(self.__ports)
        return self.__ports

    def __filterSerialPorts(self, ports):
        """
        Filters Serial Ports with valid Serial Number, VID and PID
        :param ports: List of ListPortInfo
        :return ports_filterd: List
        """
        ports_filterd = []

        for port in ports:
            if port.serial_number != None and port.serial_number != "FFFFFFFFFFFFFFFFFFFF" and port.vid != None and port.pid != None:
                ports_filterd.append(port)

        return ports_filterd

    def __transformInArancinoPorts(self, ports):
        """
        This methods creates a new structure starting from a List of ListPortInfo.
        A base element of the new structure is composed by some metadata and
        the initial object of type ListPortInfo


        :param ports: List of plugged port (ListPortInfo)
        :return: Dict of Ports with additional information
        """
        new_ports_struct = {}

        for port in ports:
            p = ArancinoPort(plugged=True, port=port)
            new_ports_struct[p.id] = p

        return new_ports_struct


class ArancinoPort:

    def __init__(self, enabled=False, auto_connect=False, alias="", plugged=False, connected=False, port=None):
        # serial port
        self.port = port

        # serial port identification
        #self.id = port.serial_number

        # configuration metadata
        self.enabled = enabled
        self.auto_connect = auto_connect
        self.alias = alias

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
