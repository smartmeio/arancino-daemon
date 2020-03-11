'''
SPDX-license-identifier: Apache-2.0

Copyright (c) 2019 SmartMe.IO

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

import os
import signal
import requests

from arancino.ArancinoUtils import ArancinoLogger
from arancino.Arancino import Arancino
from arancino.ArancinoUtils import ArancinoConfig
from arancino.utils.pam import pamAuthentication
from threading import Thread

from flask_httpauth import HTTPBasicAuth
from flask import Flask, jsonify, request



from arancino.ArancinoRestApi import ArancinoApi


auth = HTTPBasicAuth()

m = Arancino()
c = ArancinoConfig.Instance()

LOG = ArancinoLogger.Instance().getLogger()
ENV = os.environ.get('ARANCINOENV')

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    else:
        LOG.info("HTTP Server is shutting down...")
        func()

def __kill(signum, frame):
    m.stop()
    requests.post('http://0.0.0.0:1475/api/v1/shutdown-not-easy-to-find-api')
    #m.join()

def __runArancino():
    m.start()

def __runArancinoApi():

    api = ArancinoApi()

    app = Flask(__name__)

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


    @app.route('/api/v1/', methods=['GET'])
    def api_hello():

        result = api.hello()
        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/ports', methods=['GET'])
    def api_get_ports():
        result = api.getAllPorts()
        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/ports/connected', methods=['GET'])
    def api_get_ports_connected():

        result = api.getPortsConnected()
        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/ports/discovered', methods=['GET'])
    def get_ports_discovered():

        result = api.getPortsDiscovered()
        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/ports/<port_id>', methods=['GET'])
    def api_get_port(port_id):

        result = api.getPort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/ports/<port_id>/reset', methods=['POST'])
    @auth.login_required
    def api_reset(port_id=None):
        result = api.resetPort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/ports/<port_id>/enable', methods=['POST'])
    @auth.login_required
    def api_enable(port_id=None):
        result = api.enablePort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/ports/<port_id>/disable', methods=['POST'])
    @auth.login_required
    def api_disable(port_id=None):
        result = api.disablePort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/ports/<port_id>/upload', methods=['POST'])
    @auth.login_required
    def upload_file(port_id):

        # check if the post request has the file part
        if 'firmware' not in request.files:
            response = jsonify({'message': 'No file part in the request'})
            response.status_code = 400
            return response

        file = request.files['firmware']
        if file.filename == '':
            response = jsonify({'message': 'No file selected for uploading'})
            response.status_code = 400
            return response

        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            path = os.path.join(c.get_port_firmware_path(), port_id)

            if not os.path.isdir(path):
                os.makedirs(path)

            file_fw = os.path.join(path, file.filename)
            file.save(file_fw)

            result = api.uploadFirmware(port_id, file_fw)

            response = jsonify(result[0])
            response.status_code = result[1]
            return response

        else:
            response = jsonify({'message': 'Allowed file types are {}'.format(str(ALLOWED_EXTENSIONS))})
            response.status_code = 400
            return response

    @app.route('/api/v1/shutdown-not-easy-to-find-api', methods=['POST'])
    def shutdown():
        shutdown_server()
        return 'Server shutting down...'

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
