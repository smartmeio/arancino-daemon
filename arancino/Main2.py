import multiprocessing
import signal
from arancino.Arancino import Arancino
import gunicorn.app.base
from flask import Flask

m = Arancino()

def __kill(signum, frame):
    m.stop()
    m.join()

def __runArancino():
    m.start()


def number_of_workers():
    #return (multiprocessing.cpu_count() * 2) + 1
    return 1


def handler_app(environ, start_response):
    response_body = b'Works fine'
    status = '200 OK'

    response_headers = [
        ('Content-Type', 'text/plain'),
    ]

    start_response(status, response_headers)

    return [response_body]


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        pass
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    def on_exit(server):
        print("EXIT")

def __runArancinoApi():
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return "Hello World!"

    return app

if __name__ == '__main__':

    __runArancino()

    signal.signal(signal.SIGINT, __kill)
    signal.signal(signal.SIGTERM, __kill)

    options = {
        'bind': '%s:%s' % ('127.0.0.1', '8080'),
        'workers': number_of_workers(),
    }

    std = StandaloneApplication(__runArancinoApi(), options)
    std.run()



# m = Arancino()
#
# def __kill(signum, frame):
#     m.stop()
#     #m.join()
#
# def __runArancino():
#     m.start()
#
#
# def __runArancinoApi():
#     from flask import Flask
#     app = Flask(__name__)
#
#     @app.route('/')
#     def hello():
#         return "Hello World!"
#
#     app.run(host='0.0.0.0', port=1475, debug=False, use_reloader=False)
#
#
# if __name__ == '__main__':
#     __runArancino()
#
#     signal.signal(signal.SIGINT, __kill)
#     signal.signal(signal.SIGTERM, __kill)
#
#     api = Thread(name='ArancinoAPI', target=__runArancinoApi, args=())
#     api.start()
