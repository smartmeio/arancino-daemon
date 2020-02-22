



from arancino.ArancinoUtils import ArancinoConfig
# from arancino.filter import FilterTypes

from arancino.port.ArancinoTestPort import ArancinoTestPort

CONF = ArancinoConfig.Instance()

class ArancinoTestDiscovery:

    def __init__(self):
        # self.__filter = ArancinoSerialPortFilter()
        # self.__filter_type = CONF.get_port_serial_filter_type()
        # self.__filter_list = CONF.get_port_serial_filter_list()
        pass


    # TODO: this can be an abstract method
    def getAvailablePorts(self):
        """
        Create Arancino Port for test purpose
        """

        ports = {}
        num = CONF.get_port_test_num()
        tmpl_id = CONF.get_port_test_id_template()

        for count in range(1, int(num)+1):
            id = tmpl_id + str(count)

            port = ArancinoTestPort(id=id, device="There", m_s_plugged=True, m_c_enabled=CONF.get_port_test_enabled(), m_c_auto_connect=True, m_c_alias=id, m_c_hide=CONF.get_port_test_hide())
            ports[id] = port

        return ports