#!/usr/bin/env python
import logging, sys
from logging.handlers import RotatingFileHandler

#redis connection parameter
redis = {'host': 'localhost',
         'port': 6379,
         'dcd_resp': True,  #decode response
         'db': 0}

# allowed vid and pid to connect to
hwid = [
        'F00A:00FA'
        ,'2A03:804E'
        ,'2341:0043'
        ]

# logger configuration
__name = 'Arancino Serial Module'
__filename = 'arancino.log'
__format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def __get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(__format)
   return console_handler

def __get_file_handler():
   file_handler = RotatingFileHandler(__filename, mode='a', maxBytes=1*1024*1024, backupCount=5)
   file_handler.setFormatter(__format)
   return file_handler

logger = logging.getLogger(__name)

logger.setLevel(logging.DEBUG)
#logger.addHandler(__get_console_handler())
logger.addHandler(__get_file_handler())