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
import arancino.arancino_constants as const
import arancino.arancino_log_formatter as formatter
import configparser
import json

Config = configparser.ConfigParser()
Config.read(os.path.join(os.environ.get('ARANCINOCONF'),"arancino.cfg"))

#version
#version = "1.1.1"
version = Config.get("metadata", "version")

# global variables
global redis_instance, serial_baudrate 

def getRedisInstancesType():

    global redis_instance

    #if redis_instance not in const.RedisInstancesType:
    if not const.RedisInstancesType.has_value(redis_instance.value) :
        redis_instance =  const.RedisInstancesType.DEFAULT.value

    '''
    redis_dts: datastore => contains application data (default volatile)
    redis_dvs: devicestore => contains data about connected device (default persistent)
    redis_dts_rsvd: datastore persisten keys => contains application data which must be available after device reboot or application restart (default persistent)
    '''
    if redis_instance == const.RedisInstancesType.VOLATILE:
        redis_dts = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 0}
        redis_dvs = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 1}
        redis_dts_rsvd = {'host': 'localhost', 'port': 6379, 'dcd_resp': True,'db': 2}

    elif redis_instance == const.RedisInstancesType.PERSISTENT:
        redis_dts = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 0}
        redis_dvs = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 1}
        redis_dts_rsvd = {'host': 'localhost', 'port': 6380, 'dcd_resp': True,'db': 2}

    elif redis_instance == const.RedisInstancesType.VOLATILE_PERSISTENT: 
        redis_dts = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 0}
        redis_dvs = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 0}
        redis_dts_rsvd = {'host': 'localhost', 'port': 6380, 'dcd_resp': True,'db': 1}

    else: # DEFAULT is VOLATILE_PERSISTENT
        redis_dts = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 0}
        redis_dvs = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 0}
        redis_dts_rsvd = {'host': 'localhost', 'port': 6380, 'dcd_resp': True,'db': 1}

    return redis_dts, redis_dvs, redis_dts_rsvd


# redis instance type
redis_instance = const.RedisInstancesType[Config["redis"].get("instance_type")]

# serial baud rate
#serial_baudrate = const.SerialBaudrates._4000000
serial_baudrate = Config["port"].getint("baudrate")

def getSerialBaudrate():
    
    global serial_baudrate
    
    return serial_baudrate
    #return serial_baudrate.value

#cycle interval time
cycle_time = Config["general"].getint("cycle_time")#int(Config.get("general","cycle_time"))

# default arancino port configuration
port = {
    'enabled': Config["port"].getboolean("enabled"),#True,
    'auto_connect': Config["port"].getboolean("auto_connect"),#False,
    'hide': Config["port"].getboolean("hide")#False
}

# allowed vid and pid to connect to
'''
hwid = [
        'F00A:00FA'
        ,'2A03:804E'
        ,'2341:0043'
        ]
'''
hwid = json.loads(Config["general"].get("allowed_hwid"))

# logger configuration
__name = Config["log"].get("name")              #'Arancino Serial'
__filename = Config["log"].get("log")           #'arancino.log'
__error_filename = Config["log"].get("error")   #'arancino.error.log'
__stats_filename = Config["log"].get("stats")   #'arancino.stats.log'
#__dirlog = Config["log"].get("path")           #'/var/log/arancino'
__dirlog = os.environ.get('ARANCINOLOG')
__format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_stats_file_path():
    return os.path.join(__dirlog, __stats_filename)

def __get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(formatter.CustomConsoleFormatter())
   return console_handler

def __get_file_handler():
   file_handler = RotatingFileHandler(os.path.join(__dirlog, __filename), mode='a', maxBytes=1000*1024, backupCount=5)
   file_handler.setFormatter(__format)
   return file_handler

def __get_error_file_handler():
    file_handler_error = RotatingFileHandler(os.path.join(__dirlog, __error_filename), mode='a', maxBytes=1000*1024, backupCount=5)
    file_handler_error.setFormatter(__format)
    file_handler_error.setLevel(logging.ERROR)
    return file_handler_error

logger = logging.getLogger(__name)
logger.setLevel( logging.getLevelName(Config["log"].get("level")) )
logger.addHandler(__get_file_handler())
logger.addHandler(__get_error_file_handler())

if Config["log"].get("console").upper() == "TRUE":
    logger.addHandler(__get_console_handler())
