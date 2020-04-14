# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2020 SmartMe.IO

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
"""


import configparser
import logging
import sys
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler

import semantic_version

from arancino.ArancinoConstants import RedisInstancesType
from arancino.filter.ArancinoPortFilter import FilterTypes

class Singleton:

    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@Singleton
class ArancinoConfig:

    def __init__(self):

        env = os.environ.get('ARANCINOENV')
        if env.upper() == "DEV" or env.upper() == "TEST" or env.upper() == "DEBUG" or env.upper() == "DEVELOPMENT":
            cfg_file = "arancino.test.cfg"
        elif env.upper() == "PROD" or env.upper() == "PRODUCTION":
            cfg_file = "arancino.cfg"

        Config = configparser.ConfigParser()
        Config.read(os.path.join(os.environ.get('ARANCINOCONF'), cfg_file))

        # CONFIG METADATA SECTION
        self.__metadata_version = semantic_version.Version(Config.get("metadata", "version"))

        # CONFIG GENERAL SECTION
        self.__general_env = env
        self.__general_cycle_time = int(Config.get("general", "cycle_time"))
        #self.__general_users = Config.get("general", "users")

        # CONFIG REDIS SECTION
        self.__redis_instance_type = Config.get("redis", "instance_type")
        self.__redis_connection_attempts = int(Config.get("redis", "connection_attempts"))

        self.__redis_host = Config.get("redis", "host")
        self.__redis_port_volatile = Config.get("redis", "port_volatile")
        self.__redis_port_persistent = Config.get("redis", "port_persistent")
        self.__redis_decode_response = stringToBool(Config.get("redis", "decode_response"))

        self.__redis_volatile_datastore_std_db = int(Config.get("redis.volatile", "datastore_std_db"))
        self.__redis_volatile_datastore_dev_db = int(Config.get("redis.volatile", "datastore_dev_db"))
        self.__redis_volatile_datastore_per_db = int(Config.get("redis.volatile", "datastore_per_db"))

        self.__redis_persistent_datastore_std_db = int(Config.get("redis.persistent", "datastore_std_db"))
        self.__redis_persistent_datastore_dev_db = int(Config.get("redis.persistent", "datastore_dev_db"))
        self.__redis_persistent_datastore_per_db = int(Config.get("redis.persistent", "datastore_per_db"))

        self.__redis_volatile_persistent_datastore_std_db = int(Config.get("redis.volatile_persistent", "datastore_std_db"))
        self.__redis_volatile_persistent_datastore_dev_db = int(Config.get("redis.volatile_persistent", "datastore_dev_db"))
        self.__redis_volatile_persistent_datastore_per_db = int(Config.get("redis.volatile_persistent", "datastore_per_db"))



        # CONFIG PORT SECTION
        self.__port_firmware_path = Config.get("port", "firmware_path")
        self.__port_firmware_file_types = Config.get("port", "firmware_file_types")

        # CONFIG SERIAL PORT SECTION
        self.__port_serial_enabled = stringToBool(Config.get("port.serial", "enabled"))
        self.__port_serial_hide = stringToBool(Config.get("port.serial", "hide"))
        self.__port_serial_comm_baudrate = int(Config.get("port.serial", "comm_baudrate"))
        self.__port_serial_reset_baudrate = int(Config.get("port.serial", "reset_baudrate"))
        self.__port_serial_filter_type = Config.get("port.serial", "filter_type")
        self.__port_serial_filter_list = Config.get("port.serial", "filter_list")
        self.__port_serial_upload_command = Config.get("port.serial", "upload_command")
        self.__port_serial_timeout = int(Config.get("port.serial", "timeout"))

        # CONFIG TEST PORT SECTION
        self.__port_test_enabled = stringToBool(Config.get("port.test", "enabled"))
        self.__port_test_hide = stringToBool(Config.get("port.test", "hide"))
        self.__port_test_filter_type = Config.get("port.test", "filter_type")
        self.__port_test_filter_list = Config.get("port.test", "filter_list")
        self.__port_test_num = int(Config.get("port.test", "num"))
        self.__port_test_delay = float(Config.get("port.test", "delay"))
        self.__port_test_id_template = Config.get("port.test", "id_template")
        self.__port_test_upload_command = Config.get("port.test", "upload_command")

        # CONFIG LOG SECTION
        self.__log_level = Config.get("log", "level")
        self.__log_name = Config.get("log", "name")
        self.__log_size = int(Config.get("log", "size")) if 0 < int(Config.get("log", "size")) <= 5 else 1
        self.__log_rotate = int(Config.get("log", "rotate")) if 0 < int(Config.get("log", "rotate")) <= 10 else 1

        self.__log_handler_console = stringToBool(Config.get("log", "handler_console"))
        self.__log_handler_file = stringToBool(Config.get("log", "handler_file"))

        self.__log_file_log = Config.get("log", "file_log")
        #self.__log_file_api = Config.get("log", "file_base")
        self.__log_file_error = Config.get("log", "file_error")
        #self.__log_file_stats = Config.get("log", "file_stats")


        self.__dirlog = os.environ.get('ARANCINOLOG')

    ######## METADATA ########
    def get_metadata_version(self):
        return self.__metadata_version

    ######## GENERAL ########
    def get_general_env(self):
        return self.__general_env

    def get_general_cycle_time(self):
        return self.__general_cycle_time

    # def get_general_users(self):
    #     return json.loads(self.__general_users)


    ######## REDIS ########
    def get_redis_instances_conf(self):

        # redis instance type
        #if not RedisInstancesType.has_value(self.__redis_instance_type):
        #    redis_instance = RedisInstancesType.DEFAULT.value

        if self.__redis_instance_type not in RedisInstancesType.__members__:
            redis_instance = RedisInstancesType.DEFAULT.value
        else:
            redis_instance = RedisInstancesType[self.__redis_instance_type]

        '''
        redis_dts_std: standard datastore => contains application data (default volatile)
        redis_dts_dev: device data store => contains data about connected device (default persistent)
        redis_dts_per: persistent data store => contains application data which must be available after device reboot or application restart (default persistent)
        '''
        # DEFAULT -> VOLATILE PERSISTENT
        host = self.__redis_host
        dec_rsp = self.__redis_decode_response

        if redis_instance == RedisInstancesType.VOLATILE:
            port_vol = self.__redis_port_volatile
            port_per = self.__redis_port_volatile
            dts_std_db = self.__redis_volatile_datastore_std_db
            dts_per_db = self.__redis_volatile_datastore_per_db
            dts_dev_db = self.__redis_volatile_datastore_dev_db

        elif redis_instance == RedisInstancesType.PERSISTENT:
            port_vol = self.__redis_port_persistent
            port_per = self.__redis_port_persistent
            dts_std_db = self.__redis_persistent_datastore_std_db
            dts_per_db = self.__redis_persistent_datastore_per_db
            dts_dev_db = self.__redis_persistent_datastore_dev_db

        elif redis_instance == RedisInstancesType.VOLATILE_PERSISTENT:
            port_vol = self.__redis_port_volatile
            port_per = self.__redis_port_persistent
            dts_std_db = self.__redis_volatile_persistent_datastore_std_db
            dts_per_db = self.__redis_volatile_persistent_datastore_per_db
            dts_dev_db = self.__redis_volatile_persistent_datastore_dev_db

        else:  # DEFAULT is VOLATILE_PERSISTENT
            port_vol = self.__redis_port_volatile
            port_per = self.__redis_port_persistent
            dts_std_db = self.__redis_volatile_persistent_datastore_std_db
            dts_per_db = self.__redis_volatile_persistent_datastore_per_db
            dts_dev_db = self.__redis_volatile_persistent_datastore_dev_db

        redis_dts_std = {'host': host, 'port': port_vol, 'dcd_resp': dec_rsp, 'db': dts_std_db}
        redis_dts_dev = {'host': host, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_dev_db}
        redis_dts_per = {'host': host, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_per_db}

        return redis_dts_std, redis_dts_dev, redis_dts_per


    def get_redis_connection_attempts(self):
        return self.__redis_connection_attempts


    ####### PORT #######
    def get_port_firmware_path(self):
        return self.__port_firmware_path

    def get_port_firmware_file_types(self):
        return json.loads(self.__port_firmware_file_types)


    ######## SERIAL PORT ########
    def get_port_serial_enabled(self):
        return self.__port_serial_enabled

    # def get_port_serial_auto_connect(self):
    #     return self.__port_serial_auto_connect

    def get_port_serial_hide(self):
        return self.__port_serial_hide

    def get_port_serial_comm_baudrate(self):
        return self.__port_serial_comm_baudrate

    def get_port_serial_reset_baudrate(self):
        return self.__port_serial_reset_baudrate

    def get_port_serial_filter_type(self):
        if self.__port_serial_filter_type not in FilterTypes.__members__:
            return FilterTypes.DEFAULT.value
        else:
            return FilterTypes[self.__port_serial_filter_type]

    def get_port_serial_filter_list(self):
        return json.loads(self.__port_serial_filter_list.upper())

    def get_port_serial_upload_command(self):
        return self.__port_serial_upload_command

    def get_port_serial_timeout(self):
        return self.__port_serial_timeout


    ######## TEST PORT ########
    def get_port_test_enabled(self):
        return self.__port_test_enabled

    def get_port_test_hide(self):
        return self.__port_test_hide

    def get_port_test_filter_type(self):
        if self.__port_test_filter_type not in FilterTypes.__members__:
            return FilterTypes.DEFAULT.value
        else:
            return FilterTypes[self.__port_test_filter_type]

    def get_port_test_filter_list(self):
        return json.loads(self.__port_test_filter_list.upper())

    def get_port_test_num(self):
        return self.__port_test_num

    def get_port_test_delay(self):
        return self.__port_test_delay

    def get_port_test_id_template(self):
        return self.__port_test_id_template

    def get_port_test_upload_command(self):
        return self.__port_test_upload_command


    ######## LOG ########
    def get_log_level(self):
        return self.__log_level

    def get_log_name(self):
        return self.__log_name

    def get_log_size(self):
        return self.__log_size

    def get_log_rotate(self):
        return self.__log_rotate

    def get_log_handler_console(self):
        return self.__log_handler_console

    def get_log_handler_file(self):
        return self.__log_handler_file

    def get_log_file_log(self):
        return self.__log_file_log

    def get_log_file_error(self):
        return self.__log_file_error

    # def get_log_file_stats(self):
    #     return self.__log_file_stats
    #
    # def get_stats_file_path(self):
    #     return os.path.join(self.__dirlog, self.__log_file_stats)

@Singleton
class ArancinoLogger:

    def __init__(self):
        self.__logger = None

        # logger configuration
        CONF = ArancinoConfig.Instance()

        self.__name = CONF.get_log_name()  # 'Arancino Serial'
        self.__filename = CONF.get_log_file_log()  # 'arancino.log'
        self.__error_filename = CONF.get_log_file_error()  # 'arancino.error.log'
        # self.__stats_filename = conf.get_log_stats_file()  # 'arancino.stats.log'

        # __dirlog = Config["log"].get("path")           #'/var/log/arancino'
        self.__dirlog = os.environ.get('ARANCINOLOG')
        self.__format = CustomConsoleFormatter(level='DEBUG')  #logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.__log_size = CONF.get_log_size()
        self.__log_rotate = CONF.get_log_rotate()

        # logging.basicConfig(level=logging.getLevelName(CONF.get_log_level()))
        # if CONF.get_log_handler_console():
        #     logging.handlers


        self.__logger = logging.getLogger(self.__name) #CustomLogger(self.__name)#
        self.__logger.setLevel(logging.getLevelName(CONF.get_log_level()))

        if CONF.get_log_handler_console():
            self.__logger.addHandler(self.__getConsoleHandler())

        if CONF.get_log_handler_file():
            self.__logger.addHandler(self.__getFileHandler())
            self.__logger.addHandler(self.__getErrorFileHandler())

    def __getConsoleHandler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.__format)
        return console_handler

    def __getFileHandler(self):
        file_handler = RotatingFileHandler(os.path.join(self.__dirlog, self.__filename), mode='a', maxBytes=1000 * 1024 * self.__log_size, backupCount=self.__log_rotate)
        file_handler.setFormatter(self.__format)
        return file_handler

    def __getErrorFileHandler(self):
        file_handler_error = RotatingFileHandler(os.path.join(self.__dirlog, self.__error_filename), mode='a', maxBytes=1000 * 1024 * self.__log_size, backupCount=self.__log_rotate)
        file_handler_error.setFormatter(self.__format)
        file_handler_error.setLevel(logging.ERROR)
        return file_handler_error

    def getLogger(self):
        return self.__logger
        # return logging


# class CustomLogger(logging.Logger):
#
#
#     def debug(self, msg, *args, **kwargs):
#
#         if self.isEnabledFor(logging.DEBUG):
#             self._log(logging.DEBUG, msg, args, **kwargs)
#
#     def error(self, msg, *args, **kwargs):
#
#         if self.isEnabledFor(logging.DEBUG):
#             self._log(logging.DEBUG, msg, args, **kwargs)
#


class CustomConsoleFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    """Based on https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level"""


    def __init__(self, level="INFO"):
        self.__level = level

        format_pre = "%(asctime)s - %(name)s : %(filename)s: - "
        format_post = "%(levelname)s - %(message)s"

        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        blue = '\x1b[94:21m'
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"

        #format_pre = "%(asctime)s - %(name)s - "
        if self.__level.upper() == 'DEBUG':
            format_pre = "%(asctime)s - %(name)s : %(threadName)s.%(filename)s.%(funcName)s:%(lineno)d - "


        self.FORMATS = {
            logging.DEBUG: format_pre + grey + format_post + reset,
            logging.INFO: format_pre + blue + format_post + reset,
            logging.WARNING: format_pre + yellow + format_post + reset,
            logging.ERROR: format_pre + red + format_post + reset,
            logging.CRITICAL: format_pre + bold_red + format_post + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)




def stringToBool(value):
    '''
    Convert a string representation of boolean value to an object of type Bool.
    :param value: {String) Value to convert
    :return: {Bool} Boolean conversion
    '''
    if value is not None:
        __val = (value.upper() == "TRUE")
    else:
        __val = False

    return __val


def stringToDatetime(dt_str):
    dt = datetime.strptime(dt_str, "%Y.%m.%d %H:%M:%S")
    return dt


def datetimeToString(dt):
    dt_str = dt.strftime("%Y.%m.%d %H:%M:%S")
    return dt_str


def getProcessUptime(total_seconds):
    # https://thesmithfam.org/blog/2005/11/19/python-uptime-script/

    # Helper vars:
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24

    # Get the days, hours, etc:
    days = int(total_seconds / DAY)
    hours = int((total_seconds % DAY) / HOUR)
    minutes = int((total_seconds % HOUR) / MINUTE)
    seconds = int(total_seconds % MINUTE)

    # Build up the pretty string (like this: "N days, N hours, N minutes, N seconds")
    string = ""
    if days > 0:
        string += str(days) + " " + (days == 1 and "day" or "days") + ", "
    if len(string) > 0 or hours > 0:
        string += str(hours) + " " + (hours == 1 and "hour" or "hours") + ", "
    if len(string) > 0 or minutes > 0:
        string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes") + ", "
    string += str(seconds) + " " + (seconds == 1 and "second" or "seconds")

    return string
    #return string


# from timestampt to datetime
'''
from datetime import datetime

timestamp = 1545730073
dt_object = datetime.fromtimestamp(timestamp)

print("dt_object =", dt_object)
print("type(dt_object) =", type(dt_object))

'''

# from datetime to timestamp
'''
from datetime import datetime

# current date and time
now = datetime.now()

timestamp = datetime.timestamp(now)
print("timestamp =", timestamp)


'''