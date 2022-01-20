from arancino.utils.ArancinoUtils import ArancinoLogger
from gunicorn.glogging import Logger



class GunicornLogger(Logger):
    def setup(self, cfg):
        super().setup(cfg)
        self.access_log = ArancinoLogger.Instance().getLogger()
        self.error_log = ArancinoLogger.Instance().getLogger()

bind = '0.0.0.0:1475'
workers = 1
worker_class = 'arancino.SecWorker.CustomWorker'
timeout = 30
keepalive = 2
##keyfile = 
##certfile = 
##ca_certs = 
cert_reqs = True
do_handshake_on_connect = True




logger_class = GunicornLogger
# errorlog = os.path.join(os.getenv('ARANCINOLOG'), 'arancino.error.log')
# loglevel = 'info'
# accesslog = os.path.join(os.getenv('ARANCINOLOG'), 'arancino.log')
daemon = False