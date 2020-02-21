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
from logging.handlers import RotatingFileHandler
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

        Config = configparser.ConfigParser()
        Config.read(os.path.join(os.environ.get('ARANCINOCONF'), "arancino.cfg"))

        # CONFIG METADATA SECTION
        self.__metadata_version = Config.get("metadata", "version")

        # CONFIG GENERAL SECTION
        self.__general_env = Config.get("general", "env")
        self.__general_cycle_time = Config.get("general", "cycle_time")
        self.__general_allowed_hwid = Config.get("general", "allowed_hwid")

        # CONFIG REDIS SECTION
        self.__redis_instance_type = Config.get("redis", "instance_type")
        # TODO calcolare i parametri di connessione.

        # CONFIG SERIAL PORT SECTION
        self.__port_serial_enabled = Config.get("port.serial", "enabled")
        self.__port_serial_auto_connect = Config.get("port.serial", "auto_connect")
        self.__port_serial_hide = Config.get("port.serial", "hide")
        self.__port_serial_comm_baudrate = Config.get("port.serial", "comm_baudrate")
        self.__port_serial_reset_baudrate = Config.get("port.serial", "reset_baudrate")
        self.__port_serial_filter_type = Config.get("port.serial", "filter_type")
        self.__port_serial_filter_list = Config.get("port.serial", "filter_list")

        # CONFIG TEST PORT SECTION
        self.__port_test_enabled = Config.get("port.test", "enabled")
        self.__port_test_hide = Config.get("port.test", "hide")
        self.__port_test_filter_type = Config.get("port.test", "filter_type")
        self.__port_test_filter_list = Config.get("port.test", "filter_list")

        # CONFIG LOG SECTION
        self.__log_level = Config.get("log", "level")
        self.__log_name = Config.get("log", "name")
        self.__log_console = Config.get("log", "console")

        self.__log_log = Config.get("log", "log")
        self.__log_error = Config.get("log", "error")
        self.__log_stats = Config.get("log", "stats")

        self.__dirlog = os.environ.get('ARANCINOLOG')

    ######## METADATA ########
    def get_metadata_version(self):
        return self.__metadata_version

    ######## GENERAL ########
    def get_general_env(self):
        return self.__general_env

    def get_general_cycle_time(self):
        return self.__general_cycle_time

    def get_general_allowed_hwid(self):
        return self.__general_allowed_hwid

    ######## REDIS ########
    def get_redis_instance_type(self):

        # redis instance type
        #if not RedisInstancesType.has_value(self.__redis_instance_type):
        #    redis_instance = RedisInstancesType.DEFAULT.value

        if self.__redis_instance_type not in RedisInstancesType.__members__:
            redis_instance = RedisInstancesType.DEFAULT.value
        else:
            redis_instance = RedisInstancesType[self.__redis_instance_type]

        '''
        redis_dts: datastore => contains application data (default volatile)
        redis_dvs: devicestore => contains data about connected device (default persistent)
        redis_dts_rsvd: datastore persisten keys => contains application data which must be available after device reboot or application restart (default persistent)
        '''
        if redis_instance == RedisInstancesType.VOLATILE:
            redis_dts = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 0}
            redis_dvs = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 1}
            redis_dts_rsvd = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 2}

        elif redis_instance == RedisInstancesType.PERSISTENT:
            redis_dts = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 0}
            redis_dvs = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 1}
            redis_dts_rsvd = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 2}

        elif redis_instance == RedisInstancesType.VOLATILE_PERSISTENT:
            redis_dts = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 0}
            redis_dvs = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 0}
            redis_dts_rsvd = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 1}

        else:  # DEFAULT is VOLATILE_PERSISTENT
            redis_dts = {'host': 'localhost', 'port': 6379, 'dcd_resp': True, 'db': 0}
            redis_dvs = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 0}
            redis_dts_rsvd = {'host': 'localhost', 'port': 6380, 'dcd_resp': True, 'db': 1}

        return redis_dts, redis_dvs, redis_dts_rsvd

    ######## SERIAL PORT ########
    def get_port_serial_enabled(self):  #TODO non usata, deve essere usata nel discovery serial
        return self.__port_serial_enabled

    def get_port_serial_auto_connect(self): # TODO non usata, deve essere usata nel discovery serial
        return self.__port_serial_auto_connect

    def get_port_serial_hide(self): # TODO non usata, deve essere usata nel discovery serial
        return self.__port_serial_hide

    def get_port_serial_comm_baudrate(self):
        return self.__port_serial_comm_baudrate

    def get_port_serial_reset_baudrate(self): # TODO non usata, deve essere usata nel discovery serial
        return self.__port_serial_reset_baudrate

    def get_port_serial_filter_type(self):
        if self.__port_serial_filter_type not in FilterTypes.__members__:
            return FilterTypes.DEFAULT.value
        else:
            return FilterTypes[self.__port_serial_filter_type]

    def get_port_serial_filter_list(self):
        return json.loads(self.__port_serial_filter_list.upper())

    ######## TEST PORT ########
    def get_port_test_enabled(self):  #TODO non usata, deve essere usata nel discovery serial
        return self.__port_test_enabled

    def get_port_test_hide(self): #TODO non usata, deve essere usata nel discovery serial
        return self.__port_test_hide

    def get_port_test_filter_type(self):
        if self.__port_test_filter_type not in FilterTypes.__members__:
            return FilterTypes.DEFAULT.value
        else:
            return FilterTypes[self.__port_test_filter_type]

    def get_port_test_filter_list(self):
        return json.loads(self.__port_test_filter_list.upper())

    ######## LOG ########
    def get_log_level(self):
        return self.__log_level

    def get_log_name(self):
        return self.__log_name

    def get_log_name(self):
        return self.__log_name

    def get_log_console(self):
        return self.__log_console

    def get_log_log_file(self):
        return self.__log_log

    def get_log_error_file(self):
        return self.__log_error

    def get_log_stats_file(self):
        return self.__log_stats

    def get_stats_file_path(self):
        return os.path.join(self.__dirlog, self.__log_stats)

@Singleton
class ArancinoLogger:

    def __init__(self):
        self.__logger = None

        # logger configuration
        conf = ArancinoConfig.Instance()

        self.__name = conf.get_log_name()  # 'Arancino Serial'
        self.__filename = conf.get_log_log_file()  # 'arancino.log'
        self.__error_filename = conf.get_log_error_file()  # 'arancino.error.log'
        #self.__stats_filename = conf.get_log_stats_file()  # 'arancino.stats.log'

        # __dirlog = Config["log"].get("path")           #'/var/log/arancino'
        self.__dirlog = os.environ.get('ARANCINOLOG')
        self.__format = CustomConsoleFormatter()  #logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.__logger = logging.getLogger(self.__name)#CustomLogger(self.__name)#
        self.__logger.setLevel(logging.getLevelName(conf.get_log_level()))
        self.__logger.addHandler(self.__getFileHandler())
        self.__logger.addHandler(self.__getErrorFileHandler())

        if conf.get_log_console():
            self.__logger.addHandler(self.__getConsoleHandler())

    def __getConsoleHandler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomConsoleFormatter())
        return console_handler

    def __getFileHandler(self):
        file_handler = RotatingFileHandler(os.path.join(self.__dirlog, self.__filename), mode='a', maxBytes=1000 * 1024, backupCount=5)
        file_handler.setFormatter(self.__format)
        return file_handler

    def __getErrorFileHandler(self):
        file_handler_error = RotatingFileHandler(os.path.join(self.__dirlog, self.__error_filename), mode='a', maxBytes=1000 * 1024, backupCount=5)
        file_handler_error.setFormatter(self.__format)
        file_handler_error.setLevel(logging.ERROR)
        return file_handler_error

    def getLogger(self):
        return self.__logger


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

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    blue = '\x1b[94:21m'
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    #format_pre = "%(asctime)s - %(name)s - "
    #format_pre = "%(asctime)s - %(name)s : %(threadName)s.%(filename)s.%(funcName)s:%(lineno)d - "
    format_pre = "%(asctime)s - %(name)s : %(threadName)s.%(filename)s: - "
    format_post ="%(levelname)s - %(message)s"

    FORMATS = {
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
