import os

bind = '0.0.0.0:1475'
workers = 1
worker_class = 'sync'
timeout = 30
keepalive = 2

errorlog = os.path.join(os.getenv('ARANCINOLOG'), 'arancino.error.log')
loglevel = 'info'
accesslog = os.path.join(os.getenv('ARANCINOLOG'), 'arancino.log')
daemon = False