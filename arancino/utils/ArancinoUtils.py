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


import logging
import sys
import os
import semantic_version
import arancino
from datetime import datetime
from logging.handlers import RotatingFileHandler
from arancino.ArancinoConstants import EnvType
import re
from typing import Any
import yaml
from yaml.parser import ParserError


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
class ArancinoEnvironment:


    def __init__(self):


        self._env = os.environ.get('ARANCINOENV')
        self._home_dir = os.environ.get('ARANCINO')
        self._cfg_dir = os.environ.get('ARANCINOCONF')
        self._log_dir = os.environ.get('ARANCINOLOG')
        self._tmplt_dir = os.path.join(self._home_dir, "templates")

        self._version = semantic_version.Version(arancino.__version__)
        self._cortex_version = semantic_version.Version(arancino.__cortex__version__)

        # Recupero il serial number / uuid dalla variabile di ambiente (quando sarà disponibile) altrimenti lo recupero dal seriale
        #   del dispositivo come veniva fatto in precedenza
        self._serial_number = os.getenv("EDGEUUID") if os.getenv("EDGEUUID") else self._retrieve_serial_number()

    @property
    def env(self):
        return self._env


    @property
    def cfg_dir(self):
        return self._cfg_dir


    @property
    def version(self):
        return self._version


    @property
    def cortex_version(self):
        return self._cortex_version


    @property
    def home_dir(self):
        return self._home_dir


    @property
    def log_dir(self):
        return self._log_dir


    @property
    def tmplt_dir(self):
        return self._tmplt_dir


    @property
    def serial_number(self):
        return self._serial_number
        #return self.__retrieve_serial_number()
    def get_metadata_cortex_version(self):
        return self.__metadata_cortex_version

    ######## GENERAL ########
    def get_general_env(self):
        return self.__general_env


    # TODO: rivedere questo metodo.
    def _retrieve_serial_number(self):
        # Extract serial from cpuinfo file

        serial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    serial = line[10:26]
            f.close()
        except Exception as ex:
            try:
                f = open('cat /sys/class/dmi/id/product_uuid')
                serial = f.readline().strip()
                f.close()
            except Exception as ex:
                serial = "ERROR000000000"

        return serial

        #return self.__getMachine_addr()

    """
    def __getMachine_addr(self):

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
        #host = self.__redis_host
        dec_rsp = self.__redis_decode_response

        if redis_instance == RedisInstancesType.VOLATILE:
            host_vol = self.__redis_host_volatile
            host_per = self.__redis_host_volatile
            port_vol = self.__redis_port_volatile
            port_per = self.__redis_port_volatile
            dts_std_db = self.__redis_volatile_datastore_std_db
            dts_per_db = self.__redis_volatile_datastore_per_db
            dts_dev_db = self.__redis_volatile_datastore_dev_db
            dts_rsvd_db = self.__redis_volatile_datastore_rsvd_db
            dts_tse_db = self.__redis_volatile_datastore_tse_db
            dts_tag_db = self.__redis_volatile_datastore_tag_db
            dts_stng_db = self.__redis_volatile_datastore_stng_db

        elif redis_instance == RedisInstancesType.PERSISTENT:
            host_vol = self.__redis_host_persistent
            host_per = self.__redis_host_persistent
            port_vol = self.__redis_port_persistent
            port_per = self.__redis_port_persistent
            dts_std_db = self.__redis_persistent_datastore_std_db
            dts_per_db = self.__redis_persistent_datastore_per_db
            dts_dev_db = self.__redis_persistent_datastore_dev_db
            dts_rsvd_db = self.__redis_persistent_datastore_rsvd_db
            dts_tse_db = self.__redis_persistent_datastore_tse_db
            dts_tag_db = self.__redis_persistent_datastore_tag_db
            dts_stng_db = self.__redis_persistent_datastore_stng_db

        elif redis_instance == RedisInstancesType.VOLATILE_PERSISTENT:
            host_vol = self.__redis_host_volatile
            host_per = self.__redis_host_persistent
            port_vol = self.__redis_port_volatile
            port_per = self.__redis_port_persistent
            dts_std_db = self.__redis_volatile_persistent_datastore_std_db
            dts_per_db = self.__redis_volatile_persistent_datastore_per_db
            dts_dev_db = self.__redis_volatile_persistent_datastore_dev_db
            dts_rsvd_db = self.__redis_volatile_persistent_datastore_rsvd_db
            dts_tse_db = self.__redis_volatile_persistent_datastore_tse_db
            dts_tag_db = self.__redis_volatile_persistent_datastore_tag_db
            dts_stng_db = self.__redis_volatile_persistent_datastore_stng_db

        else:  # DEFAULT is VOLATILE_PERSISTENT
            host_vol = self.__redis_host_volatile
            host_per = self.__redis_host_persistent
            port_vol = self.__redis_port_volatile
            port_per = self.__redis_port_persistent
            dts_std_db = self.__redis_volatile_persistent_datastore_std_db
            dts_per_db = self.__redis_volatile_persistent_datastore_per_db
            dts_dev_db = self.__redis_volatile_persistent_datastore_dev_db
            dts_rsvd_db = self.__redis_volatile_persistent_datastore_rsvd_db
            dts_tse_db = self.__redis_volatile_persistent_datastore_tse_db
            dts_tag_db = self.__redis_volatile_persistent_datastore_tag_db
            dts_stng_db = self.__redis_volatile_persistent_datastore_stng_db

        redis_dts_std = {'host': host_vol, 'port': port_vol, 'dcd_resp': dec_rsp, 'db': dts_std_db}
        redis_dts_dev = {'host': host_per, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_dev_db}
        redis_dts_per = {'host': host_per, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_per_db}
        redis_dts_rsvd = {'host': host_vol, 'port': port_vol, 'dcd_resp': dec_rsp, 'db': dts_rsvd_db}
        redis_dts_tse = {'host': host_vol, 'port': port_vol, 'dcd_resp': dec_rsp, 'db': dts_tse_db}
        redis_dts_tag = {'host': host_per, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_tag_db}
        redis_dts_stng = {'host': host_per, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_stng_db}

        return redis_dts_std, redis_dts_dev, redis_dts_per, redis_dts_rsvd, redis_dts_tse, redis_dts_tag, redis_dts_stng


    def get_redis_connection_attempts(self):
        return self.__redis_connection_attempts

    def get_redis_timeseries_retation(self):
        return self.__redis_timeseris_retention

    ####### PORT #######
    def get_port_firmware_path(self):
        return self.__port_firmware_path

    def get_port_firmware_file_types(self):
        return json.loads(self.__port_firmware_file_types)

    def get_port_reset_on_connect(self):
        return self.__port_reset_on_connect

    def get_port_reset_reconnection_delay(self):
        return self.__port_reset_reconnection_delay

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

    def get_port_serial_reset_reconnection_delay(self):
        return self.__port_serial_reset_reconnection_delay

    def get_port_serial_filter_type(self):
        if self.__port_serial_filter_type not in FilterTypes.__members__:
            return FilterTypes.DEFAULT.value
        else:
            return FilterTypes[self.__port_serial_filter_type]

    def get_port_serial_filter_list(self):
        return json.loads(self.__port_serial_filter_list.upper())

    def get_port_serial_timeout(self):
        return self.__port_serial_timeout

    def get_port_serial_reset_on_connect(self):
        return self.__port_serial_reset_on_connect

    def get_port_serial_upload_command(self):
        return self.__port_serial_upload_command

    ## RP20
    def get_port_serial_rp20_upload_command(self):
        return self.__port_serial_rp20_upload_command

    def get_port_serial_rp20_reset_reconnection_delay(self):
        return self.__port_serial_rp20_reset_reconnection_delay

    def get_port_serial_rp20_comm_baudrate(self):
        return self.__port_serial_rp20_comm_baudrate

    ## STM32
    def get_port_serial_stm32_upload_command(self):
        return self.__port_serial_stm32_upload_command

    def get_port_serial_stm32_reset_reconnection_delay(self):
        return self.__port_serial_stm32_reset_reconnection_delay

    def get_port_serial_stm32_comm_baudrate(self):
        return self.__port_serial_stm32_comm_baudrate

    ## NRF52
    def get_port_serial_nrf52_upload_command(self):
        return self.__port_serial_nrf52_upload_command

    def get_port_serial_nrf52_reset_reconnection_delay(self):
        return self.__port_serial_nrf52_reset_reconnection_delay

    def get_port_serial_nrf52_comm_baudrate(self):
        return self.__port_serial_nrf52_comm_baudrate

    ## SAMD21
    def get_port_serial_samd21_upload_command(self):
        return self.__port_serial_samd21_upload_command

    def get_port_serial_samd21_reset_reconnection_delay(self):
        return self.__port_serial_samd21_reset_reconnection_delay
    
    def get_port_serial_samd21_comm_baudrate(self):
        return self.__port_serial_samd21_comm_baudrate

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

    def get_port_test_reset_on_connect(self):
        return self.__port_test_reset_on_connect


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

    def get_log_print_stack_trace(self):
        return self.__log_print_stack_trace


    def get_config_by_name(self, section, option):
        try:

            os_type = sys.platform.lower()

            if "win" in os_type:
                command = "wmic bios get serialnumber"

            elif "linux" in os_type:
                command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"

            elif "darwin" in os_type:
                command = "ioreg -l | grep IOPlatformSerialNumber"

            return os.popen(command).read().replace("\n", "").replace("	", "").replace(" ", "")

        except Exception as ex:
            return "ERROR000000000"
    """


@Singleton
class ArancinoConfig:

    _var_matcher = re.compile(r"\${([^}^{]+)}")
    _tag_matcher = re.compile(r"[^$]*\${([^}^{]+)}.*")

    def __init__(self):
        _env = ArancinoEnvironment.Instance().env
        _cfg_dir = ArancinoEnvironment.Instance().cfg_dir
        _cfg_file = ""

        if _env.upper() == EnvType.DEV \
                or _env.upper() == EnvType.TEST \
                or _env.upper() == EnvType.DEVELOPMENT:
            _cfg_file = "arancino.dev.cfg.yml"

        elif _env.upper() == EnvType.PROD \
                or _env.upper() == EnvType.PRODUCTION:
            _cfg_file = "arancino.cfg.yml"


        self.__file = os.path.join(_cfg_dir, _cfg_file)

        self.__open()

    def _path_constructor(self, _loader: Any, node: Any):

        def parse_default_value(s):
            try:
                return int(s) if s.isdigit() else float(s) if "." in s else complex(s)
            except (ValueError, AttributeError):
                return s

        def replace_fn(match):
            envparts = f"{match.group(1)}:".split(":")
            return os.environ.get(envparts[0], envparts[1])
        return parse_default_value(self._var_matcher.sub(replace_fn, node.value))


    def __open(self):
        yaml.add_implicit_resolver("!envvar", self._tag_matcher, None, yaml.SafeLoader)
        yaml.add_constructor("!envvar", self._path_constructor, yaml.SafeLoader)
        try:
            with open(self.__file, "r") as f:
                self._cfg = yaml.safe_load(f.read())
                return  self._cfg
        except (FileNotFoundError, PermissionError, ParserError):
            return  self._cfg

    def save(self):
        with open(self.__file, 'w') as yaml_file:
            yaml.dump(self._cfg, yaml_file, default_flow_style=False)
            yaml_file.close()
        self.__open()


    @property
    def cfg(self):
        return self._cfg

@Singleton
class ArancinoLogger:

    def __init__(self):
        self.__logger = None

        # logger configuration
        CONF = ArancinoConfig.Instance().cfg
        ENV = ArancinoEnvironment.Instance()

        self.__name = CONF.get("log").get("name")
        self.__filename = CONF.get("log").get("file_log") # 'arancino.log'
        self.__error_filename = CONF.get("log").get("file_error")   # 'arancino.error.log'

        # __dirlog = Config["log"].get("path")           #'/var/log/arancino'
        self.__dirlog = ENV.log_dir     #os.environ.get('ARANCINOLOG')
        self.__format = CustomConsoleFormatter(level='DEBUG')  #logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.__log_size = CONF.get("log").get("size")
        self.__log_rotate = CONF.get("log").get("rotate")

        # logging.basicConfig(level=logging.getLevelName(CONF.get_log_level()))
        # if CONF.get_log_handler_console():
        #     logging.handlers


        self.__logger = logging.getLogger(self.__name) #CustomLogger(self.__name)#
        self.__logger.setLevel(logging.getLevelName(CONF.get("log").get("level")))

        if CONF.get("log").get("handler_console"):
            self.__logger.addHandler(self.__getConsoleHandler())

        if CONF.get("log").get("handler_file"):
            self.__logger.addHandler(self.__getFileHandler())
            self.__logger.addHandler(self.__getErrorFileHandler())

    def __getConsoleHandler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.__format)
        return console_handler

    def __getFileHandler(self):
        file_handler = RotatingFileHandler(os.path.join(self.__dirlog, self.__filename), encoding='utf-8', mode='a', maxBytes=1000 * 1024 * self.__log_size, backupCount=self.__log_rotate)
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
            format_pre = "%(asctime)s - %(name)s : [%(thread)d]%(threadName)s.%(filename)s.%(funcName)s:%(lineno)d - "


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


def stringToBool2(value):
    list_true = ["true", "1", "yes", "y", "t"]
    list_false = ["false", "0", "no", "n", "f"]

    __val = False
    if value is not None:
        v = str(value).lower()

        if v in list_true:
            __val = True
        elif v in list_false:
            __val = False
        
    return __val

def isNumber(value):
    try:
        float(value)
    except ValueError:
        return False
    return True

def stringToDatetime(dt_str):
    dt = datetime.strptime(dt_str, "%Y.%m.%d %H:%M:%S")
    return dt


def datetimeToString(dt):
    dt_str = dt.strftime("%Y.%m.%d %H:%M:%S")
    return dt_str


def secondsToHumanString(total_seconds):
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


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    #return string

