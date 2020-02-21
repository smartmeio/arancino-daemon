

from serial.tools import list_ports as list
from arancino.port.ArancinoSerialPort import *

class ArancinoSerialDiscovery:

    def __init__(self):
        pass

    # TODO: this can be an abstract method
    #def get_available_ports(self, prev_plugged, connected):
    def getAvailablePorts(self):
        """
        Using python-serial library, it scans the serial ports applies filters and then
            returns a Dictionary of ArancinoPort
        :return Dictionary of ArancinoPort
        """

        ports = list.comports()
        ports = self.__filterPorts(ports)
        #ports = self.__transform_in_arancino_ports(ports, connected)
        ports = self.__transformInArancinoPorts(ports)
        return ports

    # TODO: this can be an abstract method
    def __filterPorts(self, ports):
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
    #def __transform_in_arancino_ports(self, ports, connected):
        """
        This methods creates a new structure starting from a List of ListPortInfo.
        A base element of the new structure is composed by some metadata and
        the initial object of type ListPortInfo


        :param ports: List of plugged port (ListPortInfo)
        :return: Dict of Ports with additional information
        """
        new_ports_struct = {}

        for port in ports:

            p = ArancinoSerialPort(port_info=port, m_s_plugged=True)
            #p = ArancinoSerialPort(m_c_enabled=True, m_c_alias="ABCDEF", device="/dev/cu.usbmodem14201", baudrate=4000000, timeout=None, disconnection_handler=disconnection_handler)
            # TODO this update must be outside thi class
            #if p.id in connected:
            #    p.connected = True

            new_ports_struct[p.getId()] = p

        return new_ports_struct