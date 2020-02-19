from flask import Flask
from flask import request

class ArancinoApi():

    app = None
    arancinoContext = None

    def __init__(self, __name__, arancinoContext):

        self.app = Flask(__name__)
        self.arancinoContext = arancinoContext
        self.app.add_url_rule("/arancino/v1.0/ports", "get_ports", lambda: get_ports(self.arancinoContext), methods=["GET"])
        self.app.add_url_rule("/arancino/v1.0/shutdown", "shutdown", shutdown, methods=["GET"])

    def start(self):
        self.app.run()

    def stop(self):
        import urllib.request
        urllib.request.urlopen("http://localhost:5000/arancino/v1.0/shutdown").read()

    def setArancinoContext(self, arancinoContext):
        self.arancinoContext = arancinoContext

def get_ports(arancinoContext):
    print(arancinoContext["ports_plugged"])
    return 'Hello World!'



def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Exiting"
