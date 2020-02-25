from flask import Flask
from flask import request
from arancino.Arancino import Arancino



def runRestServer():
    from flask import Flask
    app = Flask(__name__)

    app.run()

    @app.route('/')
    def hello():
        return "Hello World!"





# class ArancinoApi():
#
#     app = None
#
#
#     def __init__(self, __name__):
#
#         self.app = Flask(__name__)
#         self.app.add_url_rule("/arancino/v1.0/ports", "get_ports", get_ports, methods=["GET"])
#         self.app.add_url_rule("/arancino/v1.0/shutdown", "shutdown", shutdown, methods=["GET"])
#
#         self.arancino = Arancino()
#
#
#         # signal.signal(signal.SIGINT, self.__kill)
#         # signal.signal(signal.SIGTERM, self.__kill)
#
#     def start(self):
#         self.arancino.start()
#         self.app.run()
#
#
#     def stop(self):
#         import urllib.request
#         urllib.request.urlopen("http://localhost:5000/arancino/v1.0/shutdown").read()
#
#
# def get_ports():
#     arancino = Arancino()
#     ports = arancino.getConnectedPorts()#Arancino.Instance().getConnectedPorts()
#
#     return 'Hello World!' + ports['TESTPORT1'].getId()
#
#
# def shutdown():
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()
#     return "Exiting"
