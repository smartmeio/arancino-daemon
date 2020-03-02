from arancino.Arancino import Arancino
from arancino.ArancinoUtils import ArancinoConfig, getProcessUptime
from arancino.port.ArancinoPort import PortTypes
from arancino.ArancinoConstants import ArancinoDBKeys as keys
import arancino.ArancinoRestApi as api
import signal
import json
from threading import Thread
from socket import gethostname, gethostbyname
from platform import system, release
from uptime import uptime

m = Arancino()
c = ArancinoConfig.Instance()

def __kill(signum, frame):
    m.stop()
    #m.join()

def __runArancino():
    m.start()


def __runArancinoApi():
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello():
        sys_upt = uptime()
        ara_upt = m.getUptime()
        response = {"arancino": {}}
        response["arancino"]["system"] = {}
        response["arancino"]["system"]["os"] = [system(), release()]
        response["arancino"]["system"]["network"] = [gethostname(), gethostbyname(gethostname())]
        response["arancino"]["system"]["uptime"] = [sys_upt, getProcessUptime(int(sys_upt))]

        response["arancino"]["arancino"] = {}
        response["arancino"]["arancino"]["uptime"] = [ara_upt, getProcessUptime(int(ara_upt))]
        response["arancino"]["arancino"]["version"] = str(c.get_metadata_version())

        response["arancino"]["arancino"]["ports"] = {}
        response["arancino"]["arancino"]["ports"]["connected"] = {}
        response["arancino"]["arancino"]["ports"]["discovered"] = {}
        response["arancino"]["arancino"]["ports"]["connected"]["num"] = len(m.getConnectedPorts())
        response["arancino"]["arancino"]["ports"]["discovered"]["num"] = len(m.getDiscoveredPorts())

        for type in PortTypes:

            #response["arancino"]["arancino"]["ports"]["connected"][type.name] = []
            #response["arancino"]["arancino"]["ports"]["discovered"][type.name] = []

            for id, port in m.getConnectedPorts().items():
                if type == port.getPortType():
                    if type.name not in response["arancino"]["arancino"]["ports"]["connected"]:
                        response["arancino"]["arancino"]["ports"]["connected"][type.name] = []
                    response["arancino"]["arancino"]["ports"]["connected"][type.name].append(id)

            for id, port in m.getDiscoveredPorts().items():
                if type == port.getPortType():
                    if type.name not in response["arancino"]["arancino"]["ports"]["discovered"]:
                        response["arancino"]["arancino"]["ports"]["discovered"][type.name] = []
                    response["arancino"]["arancino"]["ports"]["discovered"][type.name].append(id)

        return response


    @app.route('/ports')
    def get_ports():
        response = {"arancino": {}}
        response["arancino"]["arancino"] = {}
        response["arancino"]["arancino"]["ports"] = {}
        response["arancino"]["arancino"]["ports"]["connected"] = {}
        response["arancino"]["arancino"]["ports"]["discovered"] = {}
        response["arancino"]["arancino"]["ports"]["connected"]["num"] = len(m.getConnectedPorts())
        response["arancino"]["arancino"]["ports"]["discovered"]["num"] = len(m.getDiscoveredPorts())

        response["arancino"]["arancino"]["ports"]["discovered"] = get_ports_discovered()
        response["arancino"]["arancino"]["ports"]["connected"] = get_ports_connected()

        return response


    @app.route('/ports/connected')
    def get_ports_connected():
        return get_ports_by_status(status='connected')


    @app.route('/ports/discovered')
    def get_ports_discovered():
        return get_ports_by_status(status='discovered')


    def get_ports_by_status(status='discovered'):
        response = {"arancino": {}}
        response["arancino"]["arancino"] = {}
        response["arancino"]["arancino"]["ports"] = {}
        response["arancino"]["arancino"]["ports"][status] = {}
        for type in PortTypes:

            list = {}
            if status.upper() == 'DISCOVERED':
                list = m.getDiscoveredPorts()
            elif status.upper() == 'CONNECTED':
                list = m.getConnectedPorts()

            for id, port in list.items():
                if type == port.getPortType():
                    if type.name not in response["arancino"]["arancino"]["ports"][status]:
                        response["arancino"]["arancino"]["ports"][status][type.name] = {}

                    response["arancino"]["arancino"]["ports"][status][type.name][id] = {}
                    # BASE ARANCINO METADATA (B)Base
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.B_ID] = id
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.B_DEVICE] = port.getDevice()
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.B_PORT_TYPE] = type.name
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.B_LIB_VER] = str(port.getLibVersion())
                    # BASE ARANCINO STATUS METADATA (S)Status
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.S_CONNECTED] = port.isConnected()
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.S_PLUGGED] = port.isPlugged()
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.S_CREATION_DATE] = port.getCreationDate()
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.S_LAST_USAGE_DATE] = port.getLastUsageDate()
                    # BASE ARANCINO CONFIGURATION METADATA (C)Configuration
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.C_ENABLED] = port.isEnabled()
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.C_ALIAS] = port.getAlias()
                    response["arancino"]["arancino"]["ports"][status][type.name][id][keys.C_HIDE_DEVICE] = port.isHidden()

        return response


    app.run(host='0.0.0.0', port=1475, debug=False, use_reloader=False)


def run():
    __runArancino()

    signal.signal(signal.SIGINT, __kill)
    signal.signal(signal.SIGTERM, __kill)

    api = Thread(name='ArancinoAPI', target=__runArancinoApi, args=())
    api.start()


if __name__ == '__main__':
    run()


# TODO: il modulo ha la versione scritta su file di config e caricata dalla Classe ArancinoConfig come semplice stringa.
#  andrebbe usato la libreria semantic_versioning cosi come fatto per la Arancino Library di ogni porta.