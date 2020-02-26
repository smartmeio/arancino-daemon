from arancino.Arancino import Arancino
import arancino.ArancinoRestApi as api
import signal
from threading import Thread

m = Arancino()

def __kill(signum, frame):
    print("kill")
    m.stop()

def __runArancino():
    m.start()


def __runArancinoApi():
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return "Hello World!"

    app.run(host='0.0.0.0', port=1475, debug=False, use_reloader=False)


if __name__ == '__main__':
    __runArancino()

    signal.signal(signal.SIGINT, __kill)
    signal.signal(signal.SIGTERM, __kill)

    api = Thread(target=__runArancinoApi, args=())
    api.start()



