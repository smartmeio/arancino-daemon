'''
SPDX-license-identifier: Apache-2.0

Copyright (C) 2019 SmartMe.IO

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

import logging, sys, os
from logging.handlers import RotatingFileHandler

#version
version = "0.1.1"

#redis connection parameter

#datastore
redis_dts = {'host': 'localhost',
         'port': 6379,
         'dcd_resp': True,  #decode response
         'db': 0}

#devicestore
redis_dvs = {'host': 'localhost',
         'port': 6379,
         'dcd_resp': True,  #decode response
         'db': 1}


#cycle interval time
cycle_time = 10


# default arancino port configuration

port = {
    'enabled': True,
    'auto_connect': False,
    'hide': False
}

# allowed vid and pid to connect to
'''
hwid = [
        'F00A:00FA'
        ,'2A03:804E'
        ,'2341:0043'
        ]
'''

# logger configuration
__name = 'Arancino Serial'
__filename = 'arancino.log'
__dirlog = "/var/log/arancino"
__format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if not os.path.exists(__dirlog):
    os.makedirs(__dirlog)

def __get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(__format)
   return console_handler

def __get_file_handler():
   file_handler = RotatingFileHandler(os.path.join(__dirlog, __filename), mode='a', maxBytes=1*1024*1024, backupCount=5)
   file_handler.setFormatter(__format)
   return file_handler

logger = logging.getLogger(__name)

logger.setLevel(logging.INFO)
#logger.addHandler(__get_console_handler())
logger.addHandler(__get_file_handler())
