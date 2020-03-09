
# TODO: essendoci piu tipi di porte, esisteranno piu tipi di librerie e di conseguenza piu matrici di compatibilità.
#   si deve quindi definire una matrice di compatibilità per tipo di porta, ed il controllo di compatibilità deve essere
#   effettuato in base al tipo di porta e considerando la matrice relativa.

import os
import signal

from arancino.Arancino import Arancino
from arancino.ArancinoUtils import ArancinoConfig, getProcessUptime
from arancino.port.ArancinoPort import PortTypes
from arancino.utils.pam import pamAuthentication
from threading import Thread

from flask_httpauth import HTTPBasicAuth
from flask import Flask, jsonify, request



from arancino.ArancinoRestApi import ArancinoApi


auth = HTTPBasicAuth()

m = Arancino()
c = ArancinoConfig.Instance()

def __kill(signum, frame):
    m.stop()
    #m.join()

def __runArancino():
    m.start()


def __runArancinoApi():

    api = ArancinoApi()

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
        # sys_upt = uptime()
        # ara_upt = m.getUptime()

        # response = {
        #     "arancino": {
        #         "system": {
        #             "os" : [system(), release()],
        #             "network": [gethostname(), gethostbyname(gethostname())],
        #             "uptime": [sys_upt, getProcessUptime(int(sys_upt))]
        #         },
        #         "arancino": {
        #             "uptime" : [ara_upt, getProcessUptime(int(ara_upt))],
        #             "version": str(c.get_metadata_version()),
        #             "ports": {
        #                 "discovered": get_response_for_ports_by_status(status='discovered'),
        #                 "connected": get_response_for_ports_by_status(status='connected')
        #             }
        #         }
        #     }
        # }

        result = api.hello()
        response = jsonify(result)
        # TODO set HTTP STATUS CODE
        # resp.status_code = 201
        return response


    @app.route('/ports', methods=['GET'])
    def api_get_ports():
        result = api.getAllPorts()
        response = jsonify(result)

        # TODO set HTTP STATUS CODE
        # resp.status_code = 201
        return response


    @app.route('/ports/connected', methods=['GET'])
    def api_get_ports_connected():

        result = api.getPortsConnected()
        response = jsonify(result)

        # TODO set HTTP STATUS CODE
        # resp.status_code = 201
        return response


    @app.route('/ports/discovered', methods=['GET'])
    def get_ports_discovered():

        result = api.getPortsDiscovered()
        response = jsonify(result)

        # TODO set HTTP STATUS CODE
        # resp.status_code = 201
        return response


    @app.route('/ports/<port_id>', methods=['GET'])
    def api_get_port(port_id):

        result = api.getPort()
        response = jsonify(result)

        # TODO set HTTP STATUS CODE
        # resp.status_code = 201

        return response


    @app.route('/ports/<port_id>/reset', methods=['POST'])
    @auth.login_required
    def api_reset(port_id=None):
        result = api.resetPort(port_id)
        response = jsonify(result)
        # TODO set HTTP STATUS CODE
        #resp.status_code = 201
        return response

    @app.route('/ports/<port_id>/enable', methods=['POST'])
    @auth.login_required
    def api_enable(port_id=None):
        result = api.enablePort(port_id)
        response = jsonify(result)

        # TODO set HTTP STATUS CODE
        #resp.status_code = 201
        return response

    @app.route('/ports/<port_id>/disable', methods=['POST'])
    @auth.login_required
    def api_disable(port_id=None):
        result = api.disablePort(port_id)
        response = jsonify(result)
        # TODO set HTTP STATUS CODE

        #resp.status_code = 201
        return response

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

            resp = api.uploadFirmware(port_id, file_fw)

            resp = jsonify(resp)
            resp.status_code = 201

            return resp
        else:
            # TODO: change allowed file types dinamically
            resp = jsonify({'message': 'Allowed file types are {}'.format(str(ALLOWED_EXTENSIONS))})
            resp.status_code = 400
            return resp


    # def get_response_for_ports_by_status(status='discovered'):
    #     response = {}
    #     for type in PortTypes:
    #
    #         list = {}
    #         if status.upper() == 'DISCOVERED':
    #             list = m.getDiscoveredPorts()
    #         elif status.upper() == 'CONNECTED':
    #             list = m.getConnectedPorts()
    #
    #         for id, port in list.items():
    #             if type == port.getPortType():
    #                 if type.name not in response:
    #                     response[type.name] = []
    #
    #                 p = {}
    #                 p[id] = get_response_for_port(port)
    #
    #                 response[type.name].append(p)
    #
    #                 # response[type.name][id] = {}
    #                 # response[type.name][id] = get_response_for_port(port)
    #
    #     return response


    # def get_response_for_port(port=None):
    #     response = {}
    #
    #     if port is not None:
    #
    #         # BASE ARANCINO METADATA (B)Base
    #         response[DB_KEYS.B_ID] = port.getId()
    #         response[DB_KEYS.B_DEVICE] = port.getDevice()
    #         response[DB_KEYS.B_PORT_TYPE] = port.getPortType().name
    #         response[DB_KEYS.B_LIB_VER] = str(port.getLibVersion())
    #
    #         # BASE ARANCINO STATUS METADATA (S)Status
    #         response[DB_KEYS.S_CONNECTED] = port.isConnected()
    #         response[DB_KEYS.S_PLUGGED] = port.isPlugged()
    #         response[DB_KEYS.B_CREATION_DATE] = port.getCreationDate()
    #         response[DB_KEYS.S_LAST_USAGE_DATE] = port.getLastUsageDate()
    #
    #         # BASE ARANCINO CONFIGURATION METADATA (C)Configuration
    #         response[DB_KEYS.C_ENABLED] = port.isEnabled()
    #         response[DB_KEYS.C_ALIAS] = port.getAlias()
    #         response[DB_KEYS.C_HIDE_DEVICE] = port.isHidden()
    #
    #     return response


    # def get_response_for_port_by_id(port_id=None):
    #     response = {}
    #     port = retrieve_port_by_id(port_id)
    #     if port is not None:
    #         return get_response_for_port(port)
    #
    #     return response


    # def retrieve_port_by_id(port_id=None):
    #     port = None
    #     if port_id is not None:
    #         port = retrieve_connected_port_by_id(port_id)
    #         if port is None:
    #             port = retrieve_discovered_port_by_id(port_id)
    #         else:
    #             pass
    #
    #         # conn = m.getConnectedPorts()
    #         # disc = m.getDiscoveredPorts()
    #         # if port_id in conn:
    #         #     port = conn[port_id]
    #         # elif port_id in disc:
    #         #     port = disc[port_id]
    #
    #     return port


    def retrieve_connected_port_by_id(port_id=None):
        port = None

        if port_id is not None:
            conn = m.getConnectedPorts()
            if port_id in conn:
                port = conn[port_id]

        return port


    def retrieve_discovered_port_by_id(port_id=None):
        port = None

        if port_id is not None:
            disc = m.getDiscoveredPorts()
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
