import os
from arancino.utils.ArancinoUtils import ArancinoLogger
from gunicorn.glogging import Logger

class GunicornLogger(Logger):
    def setup(self, cfg):
        super().setup(cfg)
        self.access_log = ArancinoLogger.Instance().getLogger()
        self.error_log = ArancinoLogger.Instance().getLogger()

bind = '0.0.0.0:1475'
workers = 1
worker_class = 'sync'
timeout = 300
keepalive = 2

logger_class = GunicornLogger
# errorlog = os.path.join(os.getenv('ARANCINOLOG'), 'arancino.error.log')
# loglevel = 'info'
# accesslog = os.path.join(os.getenv('ARANCINOLOG'), 'arancino.log')
daemon = False