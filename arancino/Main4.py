import random
import signal

from flask import Flask

from arancino.Arancino import Arancino

app = Flask(__name__)
random.seed(0)


m = Arancino()

def __kill(signum, frame):
    m.stop()
    #m.join()

def __runArancino():
    m.start()


@app.route("/")
def hello():
  x = random.randint(1, 100)
  y = random.randint(1, 100)
  return str(x * y)


signal.signal(signal.SIGINT, __kill)
signal.signal(signal.SIGTERM, __kill)


def run():
    app.run(host='0.0.0.0')


if __name__ == "__main__":
  #__runArancino()
  run()