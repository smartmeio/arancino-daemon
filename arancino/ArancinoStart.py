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

from arancino.ArancinoConstants import EnvType
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoEnvironment
from arancino.Arancino import Arancino
from arancino.utils.ArancinoUtils import ArancinoConfig
from arancino.utils.pam import pamAuthentication
from threading import Thread

from flask_httpauth import HTTPBasicAuth
from flask import Flask, jsonify, request
import logging

# from gevent.pywsgi import WSGIServer
from arancino.ArancinoRestApi import ArancinoApi


auth = HTTPBasicAuth()

c = ArancinoConfig.Instance().cfg
m = Arancino()

LOG = ArancinoLogger.Instance().getLogger()
ENV = ArancinoEnvironment.Instance()

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    else:
        LOG.info("HTTP Server is shutting down...")
        func()

def __kill():
    m.stop()

def __runArancino():
    m.start()

def __get_arancinoapi_app():
    api = ArancinoApi()

    app = Flask(__name__)

    # log setup for werkzeug and flask, startig from arancino log. not the best solution....
    log_server = logging.getLogger("werkzeug")
    for handler in LOG.handlers:
        app.logger.addHandler(handler)
        log_server.addHandler(handler)

    app.logger.setLevel(logging.getLevelName(c.get('log').get('level')))
    log_server.setLevel(logging.getLevelName(c.get('log').get('level')))

    ALLOWED_EXTENSIONS = set(c.get('port').get('firmware_file_types'))

    from arancino.ArancinoDataStore import ArancinoDataStore
    __devicestore = ArancinoDataStore.Instance().getDataStoreDev()

    @auth.verify_password
    def verify(username, password):
        # if not (username and password):
        #     return False
        # return USER_DATA.get(username) == password

        #users_list = c.get_general_users()
        #if username in users_list:
        # return True
        if pamAuthentication(username, password):
            return True
        else:
            return False
        #else:
        #    return False

    if os.getenv('ARANCINOENV', 'DEV') == EnvType.DEV:
        @app.route('/api/v1/shutdown-not-easy-to-find-api', methods=['POST'])
        def shutdown():
            shutdown_server()
            return 'Server shutting down...'

    # region HTTP Endpoints
    # region Queries
    @app.route('/api/v1/', methods=['GET'])
    def api_hello():

        result = api.hello()
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/system', methods=['GET'])
    def api_system():

        result = api.system()
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/arancino', methods=['GET'])
    def api_arancino():

        result = api.arancino()
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
    def api_port_get(port_id):

        result = api.getPort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/arancino/config', methods=['GET'])
    def api_arancino_conf_get():

        """
        A json in the body is passed to obtain one o more specific configuration.
        An empty body means you get all the configurations.
        :return:
        """

        #if(request.get_json()): # una o piu conf specifica/e
        result = api.getArancinoConf(request.get_json())
        #else:   # tutte le conf.
        #    result = api.getArancinoConf()

        response = jsonify(result[0])
        response.status_code = result[1]
        return response
    # endregion

    # region Operarations ####
    @app.route('/api/v1/ports/<port_id>/reset', methods=['POST'])
    @auth.login_required
    def api_port_reset(port_id=None):
        result = api.resetPort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/ports/<port_id>/enable', methods=['POST'])
    @auth.login_required
    def api_port_enable(port_id=None):
        result = api.enablePort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/ports/<port_id>/disable', methods=['POST'])
    @auth.login_required
    def api_port_disable(port_id=None):
        result = api.disablePort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/ports/<port_id>/upload', methods=['POST'])
    @auth.login_required
    def api_port_upload_firmware(port_id):

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
            path = os.path.join(c.get("port").get("firmware_path"), port_id)

            if not os.path.isdir(path):
                os.makedirs(path)

            file_fw = os.path.join(path, file.filename)
            LOG.debug("Saving Firmware File {}".format(file_fw))
            file.save(file_fw)
            LOG.debug("Firmware File {} Saved".format(file_fw))

            result = api.uploadPortFirmware(port_id, file_fw)

            response = jsonify(result[0])
            response.status_code = result[1]
            return response

        else:
            response = jsonify({'message': 'Allowed file types are {}'.format(str(ALLOWED_EXTENSIONS))})
            response.status_code = 400
            return response

    @app.route('/api/v1/ports/<port_id>/config', methods=['POST'])
    @auth.login_required
    def api_port_config(port_id=None):
        result = api.setPortConfig(port_id, request.get_json())
        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/ports/<port_id>/hide', methods=['POST'])
    @auth.login_required
    def api_port_hide(port_id=None):
        result = api.hidePort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/ports/<port_id>/show', methods=['POST'])
    @auth.login_required
    def api_port_show(port_id=None):
        result = api.showPort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/arancino/config', methods=['POST'])
    @auth.login_required
    def api_arancino_conf_set():

        """
        section = request.args.get("section")
        option = request.args.get("option")
        value = request.args.get("value")
        result = api.setArancinoConf(section, option, value)
        """

        result = api.setArancinoConf(request.get_json())

        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/arancino/transmitter/<flow_name>/config', methods=['POST'])
    @auth.login_required
    def api_arancino_transmitter_conf_set(flow_name=None):

        result = api.setArancinoTransmitterConf(flow_name, request.get_json())

        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    @app.route('/api/v1/arancino/transmitter/<flow_name>/config', methods=['GET'])
    def api_arancino_transmitter_conf_get(flow_name=None):

        #if(request.get_json()): # una o piu conf specifica/e
        result = api.getArancinoTransmitterConf(flow_name, request.get_json())
        #else:   # tutte le conf.
        #    result = api.getArancinoConf()

        response = jsonify(result[0])
        response.status_code = result[1]
        return response


    @app.route('/api/v1/ports/<port_id>/identify', methods=['POST'])
    @auth.login_required
    def api_port_identify(port_id=None):
        result = api.identifyPort(port_id)
        response = jsonify(result[0])
        response.status_code = result[1]
        return response

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # endregion
    # endregion

    return app

app = __get_arancinoapi_app()
__runArancino()

if os.getenv('ARANCINOENV', 'DEV') == 'PROD':
    def stop_gunicorn(*args, **kwargs):
        __kill()

    signal.signal(signal.SIGINT, stop_gunicorn)
    signal.signal(signal.SIGTERM, stop_gunicorn)

def run():
    def stop_werkzeug(*args, **kwargs):
        __kill()
        requests.post('http://0.0.0.0:1475/api/v1/shutdown-not-easy-to-find-api')

    signal.signal(signal.SIGINT, stop_werkzeug)
    signal.signal(signal.SIGTERM, stop_werkzeug)

    api = Thread(name='ArancinoAPI', target=app.run, kwargs={'host': '0.0.0.0', 'port': 1475, 'use_reloader': False})
    api.start()

if __name__ == '__main__':
    run()
