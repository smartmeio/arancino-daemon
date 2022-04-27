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
import semantic_version
from ruamel.yaml import YAML
import arancino
from datetime import datetime
from logging.handlers import RotatingFileHandler
from arancino.ArancinoConstants import RedisInstancesType, EnvType
from arancino.port.ArancinoPortFilter import FilterTypes



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
        self._serial_number = self._retrieve_serial_number()

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


@Singleton
class ArancinoTransmitterConfig:

    def __init__(self):
        self.__yaml = YAML()#YAML(typ='safe', pure=True)

        _env = ArancinoEnvironment.Instance().env
        _cfg_dir = ArancinoEnvironment.Instance().cfg_dir
        _cfg_file = ""
        self.__files = []
        self._cfgs = {}

        from pathlib import Path
        for yml_path in Path(_cfg_dir).glob("transmitter.flow.*.cfg.yml"):
            self.__files.append(yml_path)

        self.__open()



    def __open(self):

        for f in self.__files:
            with open(f, "r") as ymlfile:
                #self._cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
                y = self.__yaml.load(ymlfile)
                self._cfgs[y.get("flow").get("name").lower()] = y
                ymlfile.close()


    def save(self, flow_name):
        yaml = YAML()
        file = os.path.join(ArancinoEnvironment.Instance().cfg_dir, "transmitter.flow.{}.cfg.yml".format(flow_name))
        for f in self.__files:

            if str(f) == file:
                with open(f, "w") as ymlfile:
                    yaml.dump(self._cfgs[flow_name], ymlfile)
                    ymlfile.close()
                break





    @property
    def cfgs(self):
        return self._cfgs

@Singleton
class ArancinoConfig2:

    def __init__(self):
        self.__yaml = YAML()#YAML(typ='safe', pure=True)

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



    def __open(self):
        with open(self.__file, "r") as ymlfile:
            #self._cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
            self._cfg = self.__yaml.load(ymlfile)
            ymlfile.close()

    def save(self):
        yaml = YAML()
        with open(self.__file, "w") as ymlfile:
            yaml.dump(self._cfg, ymlfile)
            ymlfile.close()

        #self.__open()


    @property
    def cfg(self):
        return self._cfg


@Singleton
class ArancinoConfig:

    def __init__(self):

        env = os.environ.get('ARANCINOENV')
        if env.upper() == "DEV" or env.upper() == "TEST" or env.upper() == "DEVELOPMENT":
            self.__cfg_file = "arancino.dev.cfg"
        elif env.upper() == "PROD" or env.upper() == "PRODUCTION":
            self.__cfg_file = "arancino.cfg"

        self.__arancino_config_path = os.environ.get('ARANCINOCONF')
        self.__arancino_home_path = os.environ.get('ARANCINO')
        self.__arancino_template_path = os.path.join(self.__arancino_home_path, "templates")

        self.Config = configparser.ConfigParser()
        self.Config.read(os.path.join(self.__arancino_config_path, self.__cfg_file))

        self.__serial_number = ArancinoEnvironment.Instance().serial_number

        # region CONFIG METADATA SECTION
        self.__metadata_version = semantic_version.Version(arancino.__version__)
        # endregion

        # region CONFIG GENERAL SECTION
        self.__general_env = env
        self.__general_cycle_time = int(self.Config.get("general", "cycle_time"))
        #self.__general_users = Config.get("general", "users")
        # endregion

        # region CONFIG REDIS SECTION
        self.__redis_instance_type = self.Config.get("redis", "instance_type")
        self.__redis_connection_attempts = int(self.Config.get("redis", "connection_attempts"))
        self.__redis_timeseris_retention = int(self.Config.get("redis", "retetion"))

        self.__redis_host_volatile = self.Config.get("redis", "host_volatile")
        self.__redis_host_persistent = self.Config.get("redis", "host_persistent")

        self.__redis_port_volatile = self.Config.get("redis", "port_volatile")
        self.__redis_port_persistent = self.Config.get("redis", "port_persistent")
        self.__redis_decode_response = stringToBool(self.Config.get("redis", "decode_response"))

        self.__redis_volatile_datastore_std_db = int(self.Config.get("redis.volatile", "datastore_std_db"))
        self.__redis_volatile_datastore_dev_db = int(self.Config.get("redis.volatile", "datastore_dev_db"))
        self.__redis_volatile_datastore_per_db = int(self.Config.get("redis.volatile", "datastore_per_db"))
        self.__redis_volatile_datastore_rsvd_db = int(self.Config.get("redis.volatile", "datastore_rsvd_db"))
        self.__redis_volatile_datastore_tse_db = int(self.Config.get("redis.volatile", "datastore_tse_db"))
        self.__redis_volatile_datastore_tag_db = int(self.Config.get("redis.volatile", "datastore_tag_db"))

        self.__redis_persistent_datastore_std_db = int(self.Config.get("redis.persistent", "datastore_std_db"))
        self.__redis_persistent_datastore_dev_db = int(self.Config.get("redis.persistent", "datastore_dev_db"))
        self.__redis_persistent_datastore_per_db = int(self.Config.get("redis.persistent", "datastore_per_db"))
        self.__redis_persistent_datastore_rsvd_db = int(self.Config.get("redis.persistent", "datastore_rsvd_db"))
        self.__redis_persistent_datastore_tse_db = int(self.Config.get("redis.persistent", "datastore_tse_db"))
        self.__redis_persistent_datastore_tag_db = int(self.Config.get("redis.volatile", "datastore_tag_db"))

        self.__redis_volatile_persistent_datastore_std_db = int(self.Config.get("redis.volatile_persistent", "datastore_std_db"))
        self.__redis_volatile_persistent_datastore_dev_db = int(self.Config.get("redis.volatile_persistent", "datastore_dev_db"))
        self.__redis_volatile_persistent_datastore_per_db = int(self.Config.get("redis.volatile_persistent", "datastore_per_db"))
        self.__redis_volatile_persistent_datastore_rsvd_db = int(self.Config.get("redis.volatile_persistent", "datastore_rsvd_db"))
        self.__redis_volatile_persistent_datastore_tse_db = int(self.Config.get("redis.volatile_persistent", "datastore_tse_db"))
        self.__redis_volatile_persistent_datastore_tag_db = int(self.Config.get("redis.volatile", "datastore_tag_db"))
        # endregion

        # region CONFIG PORT SECTION
        self.__port_firmware_path = self.Config.get("port", "firmware_path")
        self.__port_firmware_file_types = self.Config.get("port", "firmware_file_types")
        self.__port_reset_on_connect = stringToBool(self.Config.get("port", "reset_on_connect"))
        self.__port_reset_reconnection_delay = int(self.Config.get("port", "reset_reconnection_delay"))

        # region CONFIG SERIAL PORT SECTION
        self.__port_serial_enabled = stringToBool(self.Config.get("port.serial", "enabled"))
        self.__port_serial_hide = stringToBool(self.Config.get("port.serial", "hide"))
        self.__port_serial_reset_baudrate = int(self.Config.get("port.serial", "reset_baudrate"))
        self.__port_serial_filter_type = self.Config.get("port.serial", "filter_type")
        self.__port_serial_filter_list = self.Config.get("port.serial", "filter_list")
        self.__port_serial_upload_command = self.Config.get("port.serial", "upload_command")
        self.__port_serial_timeout = int(self.Config.get("port.serial", "timeout"))
        
        
        # DEFAULT 
        # reset on connect
        self.__port_serial_reset_on_connect = self.__get_or_override_bool(self.Config, "port.serial", "reset_on_connect", "port", "reset_on_connect")
        # upload command for serial port
        self.__port_serial_upload_command = self.Config.get("port.serial", "upload_command")
        # delay of reconnection after a reset 
        self.__port_serial_reset_reconnection_delay = int(self.__get_or_override_str(self.Config, "port.serial", "reset_reconnection_delay", "port", "reset_reconnection_delay" ))
        # communication baudrate
        self.__port_serial_comm_baudrate = int(self.Config.get("port.serial", "comm_baudrate"))

        # region SAMD21
        self.__port_serial_samd21_upload_command = self.__get_or_override_str(self.Config, "port.serial.samd21", "upload_command", "port.serial", "upload_command")
        self.__port_serial_samd21_reset_reconnection_delay = int(self.__get_or_override_str(self.Config, "port.serial.samd21", "reset_reconnection_delay", "port.serial", "reset_reconnection_delay" ))
        self.__port_serial_samd21_comm_baudrate = int(self.__get_or_override_str(self.Config, "port.serial.samd21", "comm_baudrate", "port.serial", "comm_baudrate" ))
        # endregion

        # region NRF52
        self.__port_serial_nrf52_upload_command = self.__get_or_override_str(self.Config, "port.serial.nrf52", "upload_command", "port.serial", "upload_command")
        self.__port_serial_nrf52_reset_reconnection_delay = int(self.__get_or_override_str(self.Config, "port.serial.nrf52", "reset_reconnection_delay", "port.serial", "reset_reconnection_delay" ))
        self.__port_serial_nrf52_comm_baudrate = int(self.__get_or_override_str(self.Config, "port.serial.nrf52", "comm_baudrate", "port.serial", "comm_baudrate" ))

        # endregion

        # region STM32
        self.__port_serial_stm32_upload_command = self.__get_or_override_str(self.Config, "port.serial.stm32", "upload_command", "port.serial", "upload_command")
        self.__port_serial_stm32_reset_reconnection_delay = int(self.__get_or_override_str(self.Config, "port.serial.stm32", "reset_reconnection_delay", "port.serial", "reset_reconnection_delay" ))
        self.__port_serial_stm32_comm_baudrate = int(self.__get_or_override_str(self.Config, "port.serial.stm32", "comm_baudrate", "port.serial", "comm_baudrate" ))
        # endregion

        # region RP20
        self.__port_serial_rp20_upload_command = self.__get_or_override_str(self.Config, "port.serial.rp20", "upload_command", "port.serial", "upload_command")
        self.__port_serial_rp20_reset_reconnection_delay = int(self.__get_or_override_str(self.Config, "port.serial.rp20", "reset_reconnection_delay", "port.serial", "reset_reconnection_delay" ))
        self.__port_serial_rp20_comm_baudrate = int(self.__get_or_override_str(self.Config, "port.serial.rp20", "comm_baudrate", "port.serial", "comm_baudrate" ))
        # endregion

        # endregion

        
        # endregion

        # region CONFIG TEST PORT SECTION
        self.__port_test_enabled = stringToBool(self.Config.get("port.test", "enabled"))
        self.__port_test_hide = stringToBool(self.Config.get("port.test", "hide"))
        self.__port_test_filter_type = self.Config.get("port.test", "filter_type")
        self.__port_test_filter_list = self.Config.get("port.test", "filter_list")
        self.__port_test_num = int(self.Config.get("port.test", "num"))
        self.__port_test_delay = float(self.Config.get("port.test", "delay"))
        self.__port_test_id_template = self.Config.get("port.test", "id_template")
        self.__port_test_upload_command = self.Config.get("port.test", "upload_command")
        self.__port_test_reset_on_connect = self.__get_or_override_bool(self.Config, "port.test", "reset_on_connect", "port", "reset_on_connect")
        # endregion
        # endregion

        # region CONFIG LOG SECTION
        self.__log_level = self.Config.get("log", "level")
        self.__log_name = self.Config.get("log", "name")
        self.__log_size = int(self.Config.get("log", "size")) if 0 < int(self.Config.get("log", "size")) <= 5 else 1
        self.__log_rotate = int(self.Config.get("log", "rotate")) if 0 < int(self.Config.get("log", "rotate")) <= 10 else 1

        self.__log_handler_console = stringToBool(self.Config.get("log", "handler_console"))
        self.__log_handler_file = stringToBool(self.Config.get("log", "handler_file"))

        self.__log_file_log = self.Config.get("log", "file_log")
        #self.__log_file_api = Config.get("log", "file_base")
        self.__log_file_error = self.Config.get("log", "file_error")
        #self.__log_file_stats = Config.get("log", "file_stats")
        self.__log_print_stack_trace = stringToBool(self.Config.get("log", "print_stack_trace"))
        # endregion

        # region TRANSMITTER SECTION
        self.__transmitter_reader_cycle_time = int(self.Config.get("transmitter.reader", "cycle_time"))
        self.__is_transmitter_enabled = stringToBool(self.Config.get("transmitter", "enabled"))
        self.__transmitter_flows = self.Config.get("transmitter", "flows")

        """
        # region TRANSMITTER PARSER
        self.__transmitter_parser_class = self.Config.get("transmitter.parser", "class")

        # region TRANSMITTER PARSER SIMPLE
        self.__transmitter_parser_template_file = self.Config.get("transmitter.parser", "file")
        # endregion

        # region TRANSMITTER PARSER S4T
        self.__transmitter_parser_s4t_db_name = self.Config.get("transmitter.parser.s4t", "db_name")
        # endregion

        # endregion

        # region TRANSMITTER SENDER
        self.__transmitter_sender_class = self.Config.get("transmitter.sender", "class")

        # region TRANSMITTER SENDER DO NOTHING
        # #####
        # endregion

        # region TRANSMITTER SENDER TCP SOCKET
        self.__transmitter_sender_tcp_socket_host = self.Config.get("transmitter.sender.tcpsocket", "host")
        self.__transmitter_sender_tcp_socket_port = int(self.Config.get("transmitter.sender.tcpsocket", "port"))
        # endregion

        # region TRANSMITTER SENDER MQTT
        self.__transmitter_sender_mqtt_use_tls = stringToBool(self.Config.get("transmitter.sender.mqtt", "use_tls"))
        self.__transmitter_sender_mqtt_qos = int(self.Config.get("transmitter.sender.mqtt", "qos"))
        self.__transmitter_sender_mqtt_retain = stringToBool(self.Config.get("transmitter.sender.mqtt", "retain"))
        self.__transmitter_sender_mqtt_topic = self.Config.get("transmitter.sender.mqtt", "topic")

            # plain
        self.__transmitter_sender_mqtt_host = self.Config.get("transmitter.sender.mqtt", "host")
        self.__transmitter_sender_mqtt_port = int(self.Config.get("transmitter.sender.mqtt", "port"))
        self.__transmitter_sender_mqtt_username = self.Config.get("transmitter.sender.mqtt", "username")
        self.__transmitter_sender_mqtt_password = self.Config.get("transmitter.sender.mqtt", "password")

            # secure
        self.__transmitter_sender_mqtt_ca_path = self.Config.get("transmitter.sender.mqtt", "ca_path")
        self.__transmitter_sender_mqtt_cert_path = self.Config.get("transmitter.sender.mqtt", "cert_path")
        self.__transmitter_sender_mqtt_key_path = self.Config.get("transmitter.sender.mqtt", "key_path")
        """


        # endregion

        # endregion
        # endregion

        self.__dirlog = os.environ.get('ARANCINOLOG')


    def __get_or_override_bool(self, cfg, mine_sect, mine_opt, main_sec, main_opt):
        val = ""
        try:
            val = cfg.get(mine_sect, mine_opt)
        except configparser.NoOptionError:
            val = cfg.get(main_sec, main_opt)
        finally:
            return stringToBool(val)

    def __get_or_override_str(self, cfg, mine_sect, mine_opt, main_sec, main_opt):
        val = ""
        try:
            val = cfg.get(mine_sect, mine_opt)
        except configparser.NoOptionError:
            val = cfg.get(main_sec, main_opt)
        finally:
            return str(val)


    def get_arancino_home_path(self):
        return self.__arancino_home_path

    def get_arancino_config_path(self):
        return self.__arancino_config_path

    def get_arancino_template_path(self):
        return self.__arancino_template_path

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


    def get_serial_number(self):
        return self.__serial_number

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

        redis_dts_std = {'host': host_vol, 'port': port_vol, 'dcd_resp': dec_rsp, 'db': dts_std_db}
        redis_dts_dev = {'host': host_per, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_dev_db}
        redis_dts_per = {'host': host_per, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_per_db}
        redis_dts_rsvd = {'host': host_vol, 'port': port_vol, 'dcd_resp': dec_rsp, 'db': dts_rsvd_db}
        redis_dts_tse = {'host': host_vol, 'port': port_vol, 'dcd_resp': dec_rsp, 'db': dts_tse_db}
        redis_dts_tag = {'host': host_per, 'port': port_per, 'dcd_resp': dec_rsp, 'db': dts_tag_db}

        return redis_dts_std, redis_dts_dev, redis_dts_per, redis_dts_rsvd, redis_dts_tse, redis_dts_tag


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
            section = section.replace('-', '.')
            val = self.Config.get(section, option)
            return val
        except configparser.NoOptionError as ex:
            return None
        except configparser.NoSectionError as ex:
            return None


    def get_config_all(self):
        result = {}
        for sec in self.Config.sections():
            result[sec] = {}
            for it in self.Config.items(sec):
                result[sec][it[0]] = it[1]

        return result

    # def test(self):
    #
    #     test = {}
    #     for sec in self.Config.sections():
    #         test[sec] = {}
    #         for it in self.Config.items(sec):
    #             test[sec][it[0]] = it[1]
    #
    #
    #     print(test)
    #     dmp = json.dumps(test);
    #     ob = json.loads(dmp)
    #     print(ob)



    def set_config_by_name(self, section, option, value):
        try:
            #section = section.replace('-', '.')
            self.Config.set(section, option, value)
            self.__write_config()
            return self.Config.get(section, option)
        except configparser.NoOptionError as ex:
            return None
        except configparser.NoSectionError as ex:
            return None

    def __write_config(self):
        filename = os.path.join(os.environ.get('ARANCINOCONF'), self.__cfg_file)
        with open(filename, 'w') as configfile:
            self.Config.write(configfile)


    ######## TRANSMITTER ########
    def is_transmitter_enabled(self):
        return self.__is_transmitter_enabled

    def get_transmitter_reader_cycle_time(self):
        return self.__transmitter_reader_cycle_time

    def get_transmitter_flows(self):
        return json.loads(self.__transmitter_flows.lower())

    """
    def get_transmitter_parser_class(self):
        return self.__transmitter_parser_class

    def get_transmitter_parser_template_file(self):
        return self.__transmitter_parser_template_file

    def get_transmitter_parser_s4t_db_name(self):
        return self.__transmitter_parser_s4t_db_name

    def get_transmitter_sender_class(self):
        return self.__transmitter_sender_class

    def get_transmitter_sender_tcp_socket_host(self):
        return self.__transmitter_sender_tcp_socket_host

    def get_transmitter_sender_tcp_socket_port(self):
        return self.__transmitter_sender_tcp_socket_port

    def get_transmitter_sender_mqtt_use_tls(self):
        return self.__transmitter_sender_mqtt_use_tls

    def get_transmitter_sender_mqtt_qos(self):
        return self.__transmitter_sender_mqtt_qos

    def get_transmitter_sender_mqtt_retain(self):
        return self.__transmitter_sender_mqtt_retain

    def get_transmitter_sender_mqtt_topic(self):
        return self.__transmitter_sender_mqtt_topic

    def get_transmitter_sender_mqtt_host(self):
        return self.__transmitter_sender_mqtt_host

    def get_transmitter_sender_mqtt_port(self):
        return self.__transmitter_sender_mqtt_port

    def get_transmitter_sender_mqtt_username(self):
        return self.__transmitter_sender_mqtt_username

    def get_transmitter_sender_mqtt_password(self):
        return self.__transmitter_sender_mqtt_password

    def get_transmitter_sender_mqtt_ca_path(self):
        return self.__transmitter_sender_mqtt_ca_path

    def get_transmitter_sender_mqtt_cert_path(self):
        return self.__transmitter_sender_mqtt_cert_path

    def get_transmitter_sender_mqtt_key_path(self):
        return self.__transmitter_sender_mqtt_key_path
    """

@Singleton
class ArancinoLogger:

    def __init__(self):
        self.__logger = None

        # logger configuration
        CONF__ = ArancinoConfig.Instance()
        CONF = ArancinoConfig2.Instance().cfg
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

        if CONF.get("log").get("lehandler_filevel"):
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

