from arancino.ArancinoExceptions import *


def exec_command_handler(id, cmd):
    print("NOW EXEC: [" + id + "]: " + cmd.getRaw())

def disconnection_handler(id):
    print("disconnect: " + id)

try:


    #port = ArancinoSerialPort(m_c_enabled=True, m_c_alias="ABCDEF", device="/dev/cu.usbmodem14201", baudrate=4000000, timeout=None, disconnection_handler=disconnection_handler)
    #port.connect()
    #print("TEST")
    import time
    #time.sleep(5)
    #port.disconnect()
    # time.sleep(3)
    # port.connect()
    # time.sleep(3)
    # port.disconnect()
    #redis = ArancinoConfig.getInstance().get_redis_instance_type()

    #TEST CONF
    #conf = ArancinoConfig.Instance()

    "TEST LOGGER"
    #LOG = ArancinoLogger.Instance().get_logger()
    #LOG.debug("DEBUG")
    #LOG.info("INFO")
    # LOG.warn("WARNING")
    # LOG.error("ERROR")
    # LOG.fatal("FATAL")

    "TEST REDIS"

    #LOG.info(redis)
    # redid_dts = ArancinoDataStore.Instance()
    # dts = redid_dts.getDataStore()
    # dts.set("a", "b")

    #discovery = ArancinoSerialDiscovery()
    #ports = discovery.get_available_ports()
    #print(ports)
    # arancino_ports = {}
    #
    # for p in ports:
    #     ap = ArancinoSerialPort()
    #     arancino_ports[p.serial_n]

    from arancino.Arancino import Arancino

    a = Arancino()
    a.start()

    # time.sleep(15)
    # p = m.getConnectedPorts()
    #
    # import json
    # j = json.dumps(p)
    # print(j)

    #m2 = Arancino()

    #a = ArancinoApi("ArancinoAPI")
    #a.start()



# CONF[DONE]
# LOGGER[DONE]
# LOG[DONE]
# SYNCH[DONE]
# DISCOVERY[DONE]
# FILTER PORT[DONE]
# EXEC COMMAND[DONE]
# RESPONSE[DONE]
# SEND RESPONSE[OK]
# REDIS CONNECTION[OK]
# ORCHESTRATOR[DONE]
# TEST PORT [DONE]
# DISCOVERY ABSTRACT [TODO]
# REST API [TODO]
# COMPATIBILITY CHECK[OK]
# RIPENSARE GLI ATTRIBUTI DELLE PORTE



except InvalidArgumentsNumberException as ex:
    # TODO
    print(ex)
except InvalidCommandException as ex:
    # TODO
    print(ex)
except Exception as ex:
    # TODO
    print(ex)

