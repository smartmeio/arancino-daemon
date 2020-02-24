

from serial.tools import list_ports as list

from arancino.ArancinoUtils import ArancinoConfig
from arancino.filter.ArancinoPortFilter import FilterTypes
from arancino.filter.ArancinoSerialPortFilter import ArancinoSerialPortFilter
from arancino.port.ArancinoSerialPort import *

CONF = ArancinoConfig.Instance()

class ArancinoSerialDiscovery:

    def __init__(self):
        self.__filter = ArancinoSerialPortFilter()
        self.__filter_type = CONF.get_port_serial_filter_type()
        self.__filter_list = CONF.get_port_serial_filter_list()


    # TODO: this can be an abstract method
    def getAvailablePorts(self):
        """
        Using python-serial library, it scans the serial ports applies filters and then
            returns a Dictionary of ArancinoPort
        :return Dictionary of ArancinoPort
        """

        ports = list.comports()
        ports = self.__preFilterPorts(ports)
        ports = self.__transformInArancinoPorts(ports)
        ports = self.__postFilterPorts(ports=ports, filter_type=self.__filter_type, filter_list=self.__filter_list)
        return ports


    def __preFilterPorts(self, ports):
        """
        Pre Filter Serial Ports with valid Serial Number, VID and PID
        :param ports: List of ListPortInfo
        :return ports_filterd: List
        """
        ports_filterd = []

        for port in ports:
            if port.serial_number != None and port.serial_number != "FFFFFFFFFFFFFFFFFFFF" and port.vid != None and port.pid != None:
                ports_filterd.append(port)

        return ports_filterd


    def __postFilterPorts(self, ports={}, filter_type=FilterTypes.ALL, filter_list=[]):

        if filter_type == FilterTypes.ONLY:
            return self.__filter.filterOnly(ports, filter_list)

        elif filter_type == FilterTypes.EXCLUDE:
            return self.__filter.filterExclude(ports, filter_list)

        elif filter_type == FilterTypes.ALL:
            return self.__filter.filterAll(ports, filter_list)


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

            p = ArancinoSerialPort(port_info=port, m_s_plugged=True, m_c_enabled=CONF.get_port_serial_enabled(), m_c_hide=CONF.get_port_serial_hide(), baudrate=CONF.get_port_serial_comm_baudrate())
            new_ports_struct[p.getId()] = p

        return new_ports_struct