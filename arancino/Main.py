
# TODO: essendoci piu tipi di porte, esisteranno piu tipi di librerie e di conseguenza piu matrici di compatibilità.
#   si deve quindi definire una matrice di compatibilità per tipo di porta, ed il controllo di compatibilità deve essere
#   effettuato in base al tipo di porta e considerando la matrice relativa.

import os
from arancino.Arancino import Arancino
from arancino.ArancinoUtils import ArancinoConfig, getProcessUptime
from arancino.port.ArancinoPort import PortTypes
from arancino.ArancinoConstants import ArancinoDBKeys as keys
import arancino.ArancinoRestApi as api
from arancino.utils.pam import pamAuthentication
import signal
import json
from threading import Thread
from socket import gethostname, gethostbyname
from platform import system, release
from uptime import uptime
from flask_httpauth import HTTPBasicAuth
from flask import Flask, jsonify, request

auth = HTTPBasicAuth()

m = Arancino()
c = ArancinoConfig.Instance()

def __kill(signum, frame):
    m.stop()
    #m.join()

def __runArancino():
    m.start()


def __runArancinoApi():

    app = Flask(__name__)
    #api = Api(app, prefix="/api/v1" )
    ALLOWED_EXTENSIONS = set(c.get_port_firmware_file_types())

    from arancino.ArancinoDataStore import ArancinoDataStore
    __devicestore = ArancinoDataStore.Instance().getDeviceStore()

    @auth.verify_password
    def verify(username, password):
        # if not (username and password):
        #     return False
        # return USER_DATA.get(username) == password

        users_list = c.get_general_users()
        if username in users_list:
            if pamAuthentication(username, password):
                return True
            else:
                return False
        else:
            False


    @app.route('/', methods=['GET'])
    def api_hello():
        sys_upt = uptime()
        ara_upt = m._api_getUptime()
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
        # response["arancino"]["arancino"]["ports"]["connected"]["num"] = len(m.getConnectedPorts())
        # response["arancino"]["arancino"]["ports"]["discovered"]["num"] = len(m.getDiscoveredPorts())

        for type in PortTypes:

            # response["arancino"]["arancino"]["ports"]["connected"][type.name] = []
            # response["arancino"]["arancino"]["ports"]["discovered"][type.name] = []

            for id, port in m._api_getConnectedPorts().items():
                if type == port.getPortType():
                    if type.name not in response["arancino"]["arancino"]["ports"]["connected"]:
                        response["arancino"]["arancino"]["ports"]["connected"][type.name] = []
                    response["arancino"]["arancino"]["ports"]["connected"][type.name].append(id)

            for id, port in m._api_getDiscoveredPorts().items():
                if type == port.getPortType():
                    if type.name not in response["arancino"]["arancino"]["ports"]["discovered"]:
                        response["arancino"]["arancino"]["ports"]["discovered"][type.name] = []
                    response["arancino"]["arancino"]["ports"]["discovered"][type.name].append(id)

        return response


    @app.route('/ports', methods=['GET'])
    def api_get_ports():
        response = {"arancino": {}}
        response["arancino"]["arancino"] = {}
        response["arancino"]["arancino"]["ports"] = {}
        response["arancino"]["arancino"]["ports"]["discovered"] = {}
        response["arancino"]["arancino"]["ports"]["connected"] = {}
        # response["arancino"]["arancino"]["ports"]["connected"]["num"] = len(m.getConnectedPorts())
        # response["arancino"]["arancino"]["ports"]["discovered"]["num"] = len(m.getDiscoveredPorts())

        response["arancino"]["arancino"]["ports"]["discovered"] = get_ports_discovered()
        response["arancino"]["arancino"]["ports"]["connected"] = api_get_ports_connected()

        return response


    @app.route('/ports/connected', methods=['GET'])
    def api_get_ports_connected():
        response = {"arancino": {}}
        response["arancino"]["arancino"] = {}
        response["arancino"]["arancino"]["ports"] = {}
        response["arancino"]["arancino"]["ports"]["connected"] = get_response_for_ports_by_status(status='connected')
        return  response


    @app.route('/ports/discovered', methods=['GET'])
    def get_ports_discovered():
        response = {"arancino": {}}
        response["arancino"]["arancino"] = {}
        response["arancino"]["arancino"]["ports"] = {}
        response["arancino"]["arancino"]["ports"]["discovered"] = get_response_for_ports_by_status(status='discovered')
        return response


    @app.route('/ports/<port_id>', methods=['GET'])
    def api_get_port(port_id):

        response = {"arancino": {}}
        response["arancino"]["arancino"] = {}
        response["arancino"]["arancino"]["port"] = {}
        response["arancino"]["arancino"]["port"] = get_response_for_port_by_id(port_id)

        return response


    @app.route('/ports/<port_id>/reset', methods=['POST'])
    @auth.login_required
    def api_reset(port_id=None):
        #port = retrieve_port_by_id(port_id)
        #port.reset()
        resp = m._api_resetPort(port_id)
        return resp


    @app.route('/ports/<port_id>/enable', methods=['POST'])
    @auth.login_required
    def api_enable(port_id=None):
        resp = m._api_enablePort(port_id)
        return resp

    @app.route('/ports/<port_id>/disable', methods=['POST'])
    @auth.login_required
    def api_disable(port_id=None):
        resp = m._api_disablePort(port_id)
        return resp

    @app.route('/ports/<port_id>/upload', methods=['POST'])
    @auth.login_required
    def upload_file(port_id):

        # check if the post request has the file part
        if 'firmware' not in request.files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        file = request.files['firmware']
        if file.filename == '':
            resp = jsonify({'message': 'No file selected for uploading'})
            resp.status_code = 400
            return resp
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            path = os.path.join(c.get_port_firmware_path(), port_id)

            if not os.path.isdir(path):
                os.makedirs(path)

            file_fw = os.path.join(path, file.filename)
            file.save(file_fw)

            #m.pause()
            #port = retrieve_connected_port_by_id(port_id)

            #change_status(port, False)
            #resp = port.upload(file_fw)

            #TODO: flash firmware.
            #   implement an upload method in ArancinoPort
            #       1. disconnect
            #       2. call runbossac (for serial port) at tty of the port
            #       3. it shoul reconnect automacically.

            resp = m._api_uploadFirmwareToPort(port_id, file_fw)

            resp = jsonify({'message': resp})
            resp.status_code = 201
            #change_status(port, True)
            #m.resume()
            return resp
        else:
            # TODO: change allowed file types dinamically
            resp = jsonify({'message': 'Allowed file types are {}'.format(str(ALLOWED_EXTENSIONS))})
            resp.status_code = 400
            return resp


    def get_response_for_ports_by_status(status='discovered'):
        response = {}
        for type in PortTypes:

            list = {}
            if status.upper() == 'DISCOVERED':
                list = m._api_getDiscoveredPorts()
            elif status.upper() == 'CONNECTED':
                list = m._api_getConnectedPorts()

            for id, port in list.items():
                if type == port.getPortType():
                    if type.name not in response:
                        response[type.name] = []

                    p = {}
                    p[id] = get_response_for_port(port)

                    response[type.name].append(p)

                    # response[type.name][id] = {}
                    # response[type.name][id] = get_response_for_port(port)

        return response


    def get_response_for_port(port=None):
        response = {}

        if port is not None:

            # BASE ARANCINO METADATA (B)Base
            response[keys.B_ID] = port.getId()
            response[keys.B_DEVICE] = port.getDevice()
            response[keys.B_PORT_TYPE] = port.getPortType().name
            response[keys.B_LIB_VER] = str(port.getLibVersion())

            # BASE ARANCINO STATUS METADATA (S)Status
            response[keys.S_CONNECTED] = port.isConnected()
            response[keys.S_PLUGGED] = port.isPlugged()
            response[keys.B_CREATION_DATE] = port.getCreationDate()
            response[keys.S_LAST_USAGE_DATE] = port.getLastUsageDate()

            # BASE ARANCINO CONFIGURATION METADATA (C)Configuration
            response[keys.C_ENABLED] = port.isEnabled()
            response[keys.C_ALIAS] = port.getAlias()
            response[keys.C_HIDE_DEVICE] = port.isHidden()

        return response


    def get_response_for_port_by_id(port_id=None):
        response = {}
        port = retrieve_port_by_id(port_id)
        if port is not None:
            return get_response_for_port(port)

        return response


    def retrieve_port_by_id(port_id=None):
        port = None
        if port_id is not None:
            port = retrieve_connected_port_by_id(port_id)
            if port is None:
                port = retrieve_discovered_port_by_id(port_id)
            else:
                pass

            # conn = m.getConnectedPorts()
            # disc = m.getDiscoveredPorts()
            # if port_id in conn:
            #     port = conn[port_id]
            # elif port_id in disc:
            #     port = disc[port_id]

        return port


    def retrieve_connected_port_by_id(port_id=None):
        port = None

        if port_id is not None:
            conn = m._api_getConnectedPorts()
            if port_id in conn:
                port = conn[port_id]

        return port


    def retrieve_discovered_port_by_id(port_id=None):
        port = None

        if port_id is not None:
            disc = m._api_getDiscoveredPorts()
            if port_id in disc:
                port = disc[port_id]

        return port


    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    app.run(host='0.0.0.0', port=1475, debug=False, use_reloader=False)


def run():
    __runArancino()

    signal.signal(signal.SIGINT, __kill)
    signal.signal(signal.SIGTERM, __kill)

    api = Thread(name='ArancinoAPI', target=__runArancinoApi, args=())
    api.start()


if __name__ == '__main__':
    run()