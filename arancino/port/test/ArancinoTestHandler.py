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

import threading

from arancino.ArancinoDataStore import ArancinoDataStore
#import random

import msgpack

from arancino.utils.ArancinoUtils import *
from arancino.port.ArancinoPort import PortTypes
from arancino.ArancinoConstants import ArancinoSpecialChars as specChars, ArancinoPortAttributes, \
    ArancinoCommandResponseCodes
from arancino.ArancinoConstants import ArancinoCommandResponseCodes as respCodes
from arancino.ArancinoConstants import ArancinoCommandErrorCodes as errorCodes
from arancino.ArancinoConstants import SUFFIX_TMSTP
from arancino.cortex.ArancinoPacket import PCK
import time

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
ENV = ArancinoEnvironment.Instance()
DATASTORE = ArancinoDataStore.Instance()

class ArancinoTestHandler(threading.Thread):

    def __init__(self, id, device, commandReceivedHandler, connectionLostHandler):

        self.__name = "{}-{}".format(self.__class__.__name__, id)
        threading.Thread.__init__(self, name=self.__name)
        self.__id = id
        self.__device = device
        self.__log_prefix = "[{} - {} at {}]".format(PortTypes(PortTypes.TEST).name, self.__id, self.__device)

        self.__commandReceivedHandler = commandReceivedHandler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connectionLostHandler = connectionLostHandler    # handler to be called when a connection is lost or stopped

        self.__command_delay = CONF.get("port").get("test").get("delay")

        self.__stop = False

        self.__command_test_list = self.__getCommnandsList()
        self.__command_test_del_list = self.__getCommnandsDelList()

        self.__th_service = threading.Thread(target=self.__service_task)
        self.__serviceStop = threading.Event()

    def run(self):
        time.sleep(1.5) # do il tempo ad Arancino di inserire la porta in lista
        cmd_test_list = self.__command_test_list[0]
        rsp_test_list = self.__command_test_list[1]
        commands_test_num = len(cmd_test_list)
        count = 0

        self.__th_service.start()

        if commands_test_num > 0:
            while not self.__stop:
                # Ricezione dati
                try:


                    raw_cmd = cmd_test_list[count]
                    #raw_rsp = rsp_test_list[count]

                    # send back the raw command
                    if self.__commandReceivedHandler is not None:
                        self.__commandReceivedHandler(raw_cmd)

                    if count == commands_test_num-1:
                        count = 0  # reset the counter and start again
                    else:
                        count += 1  # go to the next command

                    time.sleep(self.__command_delay)

                except Exception as ex:
                    # probably some I/O problem such as disconnected USB serial
                    LOG.error("{}I/O Error while reading data from test port: {}".format(self.__log_prefix, str(ex)))

                    self.__stop = True
                    break
        else:
            LOG.warning("{}No commands list defined for test port.".format(self.__log_prefix))


        self.__connection_lost()


    def __connection_lost(self):
        '''
        When a connection_lost is triggered means the connection to the serial port is lost or interrupted.
        In this case ArancinoPort (from plugged_ports) must be updated and status information stored into
        the device store.
        '''
        try:

            # before disconnect clear all test case:

            for raw_cmd in self.__command_test_del_list:
                self.__commandReceivedHandler(raw_cmd)
                time.sleep(0.25)


            LOG.warning("{}Connection lost".format(self.__log_prefix))
            if self.__connectionLostHandler is not None:
                self.__connectionLostHandler()

        except Exception as ex:
            LOG.exception("{}Error on connection lost: {}".format(self.__log_prefix, str(ex)))

    def stop(self):
        self.__stop = True
        self.__serviceStop.set()

    def __getCommnandsDelList(self):

        ### keys used:
        # <ID>_TEST_KEY
        # <ID>_TEST_PERS_KEY
        # <ID>_TEST_HSET
        list = []
        # # DEL
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_PERS_KEY" + specChars.CHR_EOT)
        # # HDEL
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_3" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_4" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_5" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_6" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_7" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_8" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_9" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_10" + specChars.CHR_EOT)
        # # DEL
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET_PERS" + specChars.CHR_EOT)
        #
        #
        # # DEL
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_2" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_3" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_1" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_2" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_3" + specChars.CHR_EOT)

        # DEL
        #list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1" + specChars.CHR_EOT)
        #list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2" + specChars.CHR_EOT)

        return list

    def __getCommnandsList(self):

        cortex_version = "1.1.0"
        PACKET = PCK.PACKET[cortex_version]

        ### keys used:
        # <ID>_TEST_KEY
        # <ID>_TEST_PERS_KEY
        # <ID>_TEST_HSET

        cmd_list = []
        rsp_list = []

        # region 0. START
        # firmware upload date time
        fw_date_str = "Oct 21 1985"
        fw_time_str = "09:00:00"
        fw_tz_str = "+0600"
        fw_datetime_str = fw_date_str + ' ' + fw_time_str + ' ' + fw_tz_str

        start_cmd = {
            PACKET.CMD.COMMAND_ID: PACKET.CMD.CMDS.START,
            PACKET.ARGUMENT: {
                PACKET.CMD.ARGUMENTS.PORT_ID: "TEST_36663",#"TEST_{}".format(random.randint(10000, 99999)),
                PACKET.CMD.ARGUMENTS.FIRMWARE.MCU_FAMILY: "Test Family",
                PACKET.CMD.ARGUMENTS.FIRMWARE.LIBRARY_VERSION: "3.0.0",
                PACKET.CMD.ARGUMENTS.FIRMWARE.NAME: "My Awesome Firmware",
                PACKET.CMD.ARGUMENTS.FIRMWARE.VERSION: "1.0.0",
                PACKET.CMD.ARGUMENTS.FIRMWARE.BUILD_TIME: fw_datetime_str,
                PACKET.CMD.ARGUMENTS.FIRMWARE.CORE_VERSION: "1.0.0",
                PACKET.CMD.ARGUMENTS.FIRMWARE.CORTEX_VERSION: cortex_version,
                PACKET.CMD.ARGUMENTS.FIRMWARE.USE_FREERTOS: 0,
                "CUSTOM_KEY_1": "CUSTOM_VALUE_1",
                "CUSTOM_KEY_2": "CUSTOM_VALUE_2"
            },
            PACKET.CONFIGURATION: {
                PACKET.CMD.CONFIGURATIONS.SECURE_MODE: 0
            }
        }

        start_rsp = {
            PACKET.RSP.RESPONSE_CODE: ArancinoCommandResponseCodes.RSP_OK,
            PACKET.ARGUMENT: {
                PACKET.RSP.ARGUMENTS.DAEMON_VERSION: str(ENV.version),
                PACKET.RSP.ARGUMENTS.DAEMON_ENVIRONMENT: str(ENV.env)
            },
            PACKET.CONFIGURATION: {
                #"ts": "<timestamp>",
                PACKET.RSP.CONFIGURATIONS.LOG_LEVEL: CONF.get("log").get("level")
            }
        }
        # endregion

        #cmd_list.append(msgpack.packb(start_cmd, use_bin_type=True))
        #rsp_list.append(msgpack.packb(start_rsp, use_bin_type=True))


        #region 1. SET
        set_cmd_appl_100 = {
            "cmd": "SET",
            "args": {
                "items": [
                    {"key": "key-1", "value": "value-1"},
                    {"key": "key-2", "value": "value-2"}
                ]
            },
            "cfg": {
                "type": "appl"
            }
        }

        set_cmd_appl_110 = {
            "C": 1,
            "A": {
                "I": [
                    {"K": "key-1", "V": "value-1"},
                    {"K": "key-2", "V": "value-2"}
                ]
            },
            "CF": {
                "T": "A"
            }
        }


        set_cmd_appl_pers_100 = {
            "cmd": "SET",
            "args": {
                "items": [
                    {"key": "key-p-1", "value": "value-1"},
                    {"key": "key-p-2", "value": "value-2"}
                ]
            },
            "cfg": {
                "pers": 1,
                "type": "appl"
            }
        }

        set_cmd_appl_pers_110 = {
            "C": 1,
            "A": {
                "I": [
                    {"K": "key-p-1", "V": "value-1"},
                    {"K": "key-p-2", "V": "value-2"}
                ]
            },
            "CF": {
                "P": 1,
                "T": "A"
            }
        }


        set_cmd_rsvd_100 = {
            "cmd": "SET",
            "args": {
                "items": [
                    {"key": "key-r-1", "value": "value-1"},
                    {"key": "key-r-2", "value": "value-2"}
                ]
            },
            "cfg": {
                "type": "rsvd"
            }
        }

        set_cmd_rsvd_110 = {
            "C": 1,
            "A": {
                "I": [
                    {"K": "key-r-1", "V": "value-1"},
                    {"K": "key-r-2", "V": "value-2"}
                ]
            },
            "CF": {
                "T": "R"
            }
        }


        set_cmd_stng_100 = {
            "cmd": "SET",
            "args": {
                "items": [
                    {"key": "key-s-1", "value": "value-1"},
                    {"key": "key-s-2", "value": "value-2"}
                ]
            },
            "cfg": {
                "type": "stng"
            }
        }

        set_cmd_stng_110 = {
            "C": 1,
            "A": {
                "I": [
                    {"K": "key-s-1", "V": "value-1"},
                    {"K": "key-s-2", "V": "value-2"}
                ]
            },
            "CF": {
                "T": "TS"
            }
        }


        set_cmd_appl_prfx_100 = {
            "cmd": "SET",
            "args": {
                "items": [
                    {"key": "key-1", "value": "value-1"},
                    {"key": "key-2", "value": "value-2"}
                ]
            },
            "cfg": {
                "type": "appl",
                "prfx": 1
            }
        }

        set_cmd_appl_prfx_110 = {
            "C": 1,
            "A": {
                "I": [
                    {"K": "key-1", "V": "value-1"},
                    {"K": "key-2", "V": "value-2"}
                ]
            },
            "CF": {
                "T": "A",
                "PX": 1
            }
        }

        #endregion
        #cmd_list.append(msgpack.packb(set_cmd_appl_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_appl_pers_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_rsvd_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_stng_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_appl_prfx_100, use_bin_type=True))

        #cmd_list.append(msgpack.packb(set_cmd_appl_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_appl_pers_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_rsvd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_stng_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_appl_prfx_110, use_bin_type=True))

        #region 2. GET

        get_cmd_100 = {
            "cmd": "GET",
            "args": {
                "items": [
                    "key-1", "key-2", "key-3" #l'ultima chiave non esiste, deve tornare None
                ]
            },
            "cfg": {
                "pers": 0,
                "type": "appl"
            }
        }

        get_cmd_110 = {
            "C": 2,
            "A": {
                "I": [
                    "key-1", "key-2", "key-3" #l'ultima chiave non esiste, deve tornare None
                ]
            },
            "CF": {
                "P": 0,
                "T": "A"
            }
        }

        get_cmd_pers_100 = {
            "cmd": "GET",
            "args": {
                "items": [
                    "key-p-1", "key-p-2"
                ]
            },
            "cfg": {
                "pers": 1,
                "type": "appl"
            }
        }

        get_cmd_pers_110 = {
            "C": 2,
            "A": {
                "I": [
                    "key-p-1", "key-p-2"
                ]
            },
            "CF": {
                "P": 1,
                "T": "A"
            }
        }

        get_cmd_mix_100 = {
            "cmd": "GET",
            "args": {
                "items": [
                    "key-1", "key-2", "key-p-1" # l'ultima chiave non verrà trovata perchè è su datastore persistent
                ]
            },
            "cfg": {
                "pers": 0,
                "type": "appl",
                "ack": 1
            }
        }

        get_cmd_mix_110 = {
            "C": 2,
            "A": {
                "I": [
                    "key-1", "key-2", "key-p-1" # l'ultima chiave non verrà trovata perchè è su datastore persistent
                ]
            },
            "CF": {
                "P": 0,
                "T": "A",
                "A": 1
            }
        }

        get_cmd_rsvd_100 = {
            "cmd": "GET",
            "args": {
                "items": [
                    "key-r-1", "key-r-2"
                ]
            },
            "cfg": {
                "type": "rsvd",
                "ack": 0 #metto ack 0, ma il demone forza e lo mette a 1, e manda la risposta.
            }
        }

        get_cmd_rsvd_110 = {
            "C": 2,
            "A": {
                "I": [
                    "key-r-1", "key-r-2"
                ]
            },
            "CF": {
                "T": "R",
                "A": 0 #metto ack 0, ma il demone forza e lo mette a 1, e manda la risposta.
            }
        }

        get_cmd_stng_100 = {
            "cmd": "GET",
            "args": {
                "items": [
                    "key-s-1", "key-s-2", "key-s-3"
                ]
            },
            "cfg": {
                "pers": 0,  #imposto la persistenza, ma deve essere scartata in quanto vale il type: stng che prevede pers: 1
                "type": "stng",
                "ack": 1
            }
        }

        get_cmd_stng_110 = {
            "C": 2,
            "A": {
                "I": [
                    "key-s-1", "key-s-2", "key-s-3"
                ]
            },
            "CF": {
                "P": 0,  #imposto la persistenza, ma deve essere scartata in quanto vale il type: stng che prevede pers: 1
                "T": "S",
                "A": 1
            }
        }

        get_cmd_prfx_100 = {
            "cmd": "GET",
            "args": {
                "items": [
                    "key-1", "key-2"
                ]
            },
            "cfg": {
                "pers": 0,  #imposto la persistenza, ma deve essere scartata in quanto vale il type: stng che prevede pers: 1
                "prfx": 1,
                "type": "appl",
                "ack": 1
            }
        }

        get_cmd_prfx_110 = {
            "C": 2,
            "A": {
                "I": [
                    "key-1", "key-2"
                ]
            },
            "CF": {
                "P": 0,  #imposto la persistenza, ma deve essere scartata in quanto vale il type: stng che prevede pers: 1
                "PX": 1,
                "T": "A",
                "A": 1
            }
        }

        # endregion

        #cmd_list.append(msgpack.packb(get_cmd_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_pers_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_mix_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_rsvd_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_pers_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_prfx_100, use_bin_type=True))

        #cmd_list.append(msgpack.packb(get_cmd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_pers_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_mix_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_rsvd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_pers_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_prfx_110, use_bin_type=True))


        #region 3. DEL
        del_cmd_100 = {
            "cmd": "DEL",
            "args": {
                "items": ["key-1", "key-2"]
            },
            "cfg": {
                "type": "appl",
                "pers": 0,
                "ack": 1
            }
        }

        del_cmd_110 = {
            "C": 3,
            "A": {
                "I": ["key-1", "key-2"]
            },
            "CF": {
                "T": "A",
                "P": 0,
                "A": 1
            }
        }

        del_cmd_pers_100 = {
            "cmd": "DEL",
            "args": {
                "items": ["key-p-1", "key-p-2"]
            },
            "cfg": {
                #"type": "appl", #questa volta commento, perche lo mette in automatico
                "pers": 0,
                "ack": 1
            }
        }

        del_cmd_pers_110 = {
            "C": 3,
            "A": {
                "I": ["key-p-1", "key-p-2"]
            },
            "CF": {
                #"type": "appl", #questa volta commento, perche lo mette in automatico
                "P": 0,
                "A": 1
            }
        }

        del_cmd_prfx_100 = {
            "cmd": "DEL",
            "args": {
                "items": ["key-1", "key-2"]
            },
            "cfg": {
                #"type": "appl", #questa volta commento, perche lo mette in automatico
                "pers": 0,
                "prfx": 1,
                "ack": 1
            }
        }

        del_cmd_prfx_110 = {
            "C": 3,
            "A": {
                "I": ["key-1", "key-2"]
            },
            "CF": {
                #"type": "appl", #questa volta commento, perche lo mette in automatico
                "P": 0,
                "PX": 1,
                "A": 1
            }
        }
        #endregion
        #cmd_list.append(msgpack.packb(del_cmd_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(del_cmd_pers_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(del_cmd_prfx_100, use_bin_type=True))

        #cmd_list.append(msgpack.packb(del_cmd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(del_cmd_pers_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(del_cmd_prfx_110, use_bin_type=True))


        #region 4. STORE
        cmd_store_100 = {
            "cmd": "STORE",
            "args": {
                "items": [
                    {"key": "key-1", "value": 1, "ts": "*"},
                    {"key": "key-2", "value": 2, "ts": "*"},
                    {"key": "key-3", "value": 3.14},
                ]
            },
            "cfg": {
                "ack": 1,
                "type": "tse",
            }
        }

        cmd_store_110 = {
            "C": 4,
            "A": {
                "I": [
                    {"K": "key-1", "V": 1, "TS": "*"},
                    {"K": "key-2", "V": 2, "TS": "*"},
                    {"K": "key-3", "V": 3.14},
                ]
            },
            "CF": {
                "A": 1,
                "T": "TS",
            }
        }

        cmd_store_prfx_100 = {
            "cmd": "STORE",
            "args": {
                "items": [
                    {"key": "key-1", "value": 1, "ts": "*"},
                    {"key": "key-2", "value": 2, "ts": "*"},
                    {"key": "key-3", "value": 3.14},
                ]
            },
            "cfg": {
                "ack": 1,
                "type": "tse"
            }
        }

        cmd_store_prfx_110 = {
            "C": 4,
            "A": {
                "I": [
                    {"K": "key-1", "V": 1, "TS": "*"},
                    {"K": "key-2", "V": 2, "TS": "*"},
                    {"K": "key-3", "V": 3.14},
                ]
            },
            "CF": {
                "A": 1,
                "T": "TS"
            }
        }
        #endregion

        #cmd_list.append(msgpack.packb(cmd_store_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(cmd_store_prfx_100, use_bin_type=True))

        #cmd_list.append(msgpack.packb(cmd_store_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(cmd_store_prfx_110, use_bin_type=True))

        # region 5. STORETAGS
        cmd_store_tag_100 = {
            "cmd": "STORETAGS",
            "args": {
                "key": "key-1",
                "items": [
                    {"tag": "tag-1", "value": "value-1"},
                    {"tag": "tag-2", "value": "value-2>"}
                ],
                "ts": ""
            },
            "cfg": {
                "ack": 1,
                "type": "tags",

            }
        }

        cmd_store_tag_110 = {
            "C": 5,
            "A": {
                "K": "key-1",
                "I": [
                    {"N": "tag-1", "V": "value-1"},
                    {"N": "tag-2", "V": "value-2>"}
                ],
                "TS": ""
            },
            "CF": {
                "A": 1,
                "T": "TT",

            }
        }
        # endregion

        #cmd_list.append(msgpack.packb(cmd_store_tag_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(cmd_store_tag_110, use_bin_type=True))


        #region 6. HSET
        hset_cmd_appl_100 = {
            "cmd": "HSET",
            "args": {
                "items": [
                    {"key": "key-h-1", "field": "field-A", "value": "value-1"},
                    {"key": "key-h-1", "field": "field-B", "value": "value-2"},
                    {"key": "key-h-2", "field": "field-A", "value": "value-3"},
                    {"key": "key-h-2", "field": "field-B", "value": "value-4"}
                ]
            },
            "cfg": {
                "type": "appl"
            }
        }

        hset_cmd_appl_110 = {
            "C": 6,
            "A": {
                "I": [
                    {"K": "key-h-1", "F": "field-A", "V": "value-1"},
                    {"K": "key-h-1", "F": "field-B", "V": "value-2"},
                    {"K": "key-h-2", "F": "field-A", "V": "value-3"},
                    {"K": "key-h-2", "F": "field-B", "V": "value-4"}
                ]
            },
            "CF": {
                "T": "A"
            }
        }


        hset_cmd_appl_pers_100 = {
            "cmd": "HSET",
            "args": {
                "items": [
                    {"key": "key-h-p-1", "field": "field-A", "value": "value-1"},
                    {"key": "key-h-p-1", "field": "field-B", "value": "value-2"},
                    {"key": "key-h-p-2", "field": "field-A", "value": "value-3"},
                    {"key": "key-h-p-2", "field": "field-B", "value": "value-4"}
                ]
            },
            "cfg": {
                "pers": 1,
                "type": "appl"
            }
        }

        hset_cmd_appl_pers_110 = {
            "C": 6,
            "A": {
                "I": [
                    {"K": "key-h-p-1", "F": "field-A", "V": "value-1"},
                    {"K": "key-h-p-1", "F": "field-B", "V": "value-2"},
                    {"K": "key-h-p-2", "F": "field-A", "V": "value-3"},
                    {"K": "key-h-p-2", "F": "field-B", "V": "value-4"}
                ]
            },
            "CF": {
                "P": 1,
                "T": "A"
            }
        }

        hset_cmd_rsvd_100 = {
            "cmd": "HSET",
            "args": {
                "items": [
                    {"key": "key-h-r-1", "field": "field-A", "value": "value-1"},
                    {"key": "key-h-r-1", "field": "field-B", "value": "value-2"},
                    {"key": "key-h-r-2", "field": "field-A", "value": "value-3"},
                    {"key": "key-h-r-2", "field": "field-B", "value": "value-4"}
                ]
            },
            "cfg": {
                "type": "rsvd"
            }
        }

        hset_cmd_rsvd_110 = {
            "C": 6,
            "A": {
                "I": [
                    {"K": "key-h-r-1", "F": "field-A", "V": "value-1"},
                    {"K": "key-h-r-1", "F": "field-B", "V": "value-2"},
                    {"K": "key-h-r-2", "F": "field-A", "V": "value-3"},
                    {"K": "key-h-r-2", "F": "field-B", "V": "value-4"}
                ]
            },
            "CF": {
                "T": "R"
            }
        }

        hset_cmd_stng_100 = {
            "cmd": "HSET",
            "args": {
                "items": [
                    {"key": "key-h-s-1", "field": "field-A", "value": "value-1"},
                    {"key": "key-h-s-1", "field": "field-B", "value": "value-2"},
                    {"key": "key-h-s-2", "field": "field-A", "value": "value-3"},
                    {"key": "key-h-s-2", "field": "field-B", "value": "value-4"}
                ]
            },
            "cfg": {
                "type": "stng"
            }
        }

        hset_cmd_stng_110 = {
            "C": 6,
            "A": {
                "I": [
                    {"K": "key-h-s-1", "F": "field-A", "V": "value-1"},
                    {"K": "key-h-s-1", "F": "field-B", "V": "value-2"},
                    {"K": "key-h-s-2", "F": "field-A", "V": "value-3"},
                    {"K": "key-h-s-2", "F": "field-B", "V": "value-4"}
                ]
            },
            "CF": {
                "T": "S"
            }
        }

        hset_cmd_prfx_100 = {
            "cmd": "HSET",
            "args": {
                "items": [
                    {"key": "key-1", "field": "field-A", "value": "value-1"},
                    {"key": "key-1", "field": "field-B", "value": "value-2"},
                    {"key": "key-2", "field": "field-A", "value": "value-3"},
                    {"key": "key-2", "field": "field-B", "value": "value-4"}
                ]
            },
            "cfg": {
                "type": "appl",
                "prfx": 1
            }
        }

        hset_cmd_prfx_110 = {
            "C": 6,
            "A": {
                "I": [
                    {"K": "key-1", "F": "field-A", "V": "value-1"},
                    {"K": "key-1", "F": "field-B", "V": "value-2"},
                    {"K": "key-2", "F": "field-A", "V": "value-3"},
                    {"K": "key-2", "F": "field-B", "V": "value-4"}
                ]
            },
            "CF": {
                "T": "A",
                "PX": 1
            }
        }
        #endregion

        #cmd_list.append(msgpack.packb(hset_cmd_appl_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_appl_pers_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_rsvd_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_stng_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_prfx_100, use_bin_type=True))

        #cmd_list.append(msgpack.packb(hset_cmd_appl_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_appl_pers_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_rsvd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_stng_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_prfx_110, use_bin_type=True))


        #region 7. HGET
        hget_cmd_100 = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-h-1", "field": "field-A"},
                    {"key": "key-h-1", "field": "field-B"},
                    {"key": "key-h-2", "field": "field-A"},
                    {"key": "key-h-2", "field": "field-B"},
                ]
            },
            "cfg": {
                "pers": 0,
                "type": "appl"
            }
        }

        hget_cmd_110 = {
            "C": 7,
            "A": {
                "I": [
                    {"K": "key-h-1", "F": "field-A"},
                    {"K": "key-h-1", "F": "field-B"},
                    {"K": "key-h-2", "F": "field-A"},
                    {"K": "key-h-2", "F": "field-B"},
                ]
            },
            "CF": {
                "P": 0,
                "T": "A"
            }
        }

        hget_cmd_pers_100 = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-h-p-1", "field": "field-A"},
                    {"key": "key-h-p-1", "field": "field-B"},
                    {"key": "key-h-p-2", "field": "field-A"},
                    {"key": "key-h-p-2", "field": "field-B"},
                ]
            },
            "cfg": {
                "pers": 1,
                "type": "appl"
            }
        }

        hget_cmd_pers_110 = {
            "C": 7,
            "A": {
                "I": [
                    {"K": "key-h-p-1", "F": "field-A"},
                    {"K": "key-h-p-1", "F": "field-B"},
                    {"K": "key-h-p-2", "F": "field-A"},
                    {"K": "key-h-p-2", "F": "field-B"},
                ]
            },
            "CF": {
                "P": 1,
                "T": "A"
            }
        }


        hget_cmd_mix_100 = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-h-1", "field": "field-A"},
                    {"key": "key-h-1", "field": "field-B"},
                    {"key": "key-h-2", "field": "field-C"},  # field-C non esiste
                    {"key": "key-h-3", "field": "field-A"}  # key-h-3 non esiste
                ]
            },
            "cfg": {
                "pers": -1,
                "type": "appl",
                "ack": 1
            }
        }

        hget_cmd_mix_110 = {
            "C": 7,
            "A": {
                "I": [
                    {"K": "key-h-1", "F": "field-A"},
                    {"K": "key-h-1", "F": "field-B"},
                    {"K": "key-h-2", "F": "field-C"},  # field-C non esiste
                    {"K": "key-h-3", "F": "field-A"}  # key-h-3 non esiste
                ]
            },
            "CF": {
                "P": -1,
                "T": "A",
                "A": 1
            }
        }

        hget_cmd_rsvd_100 = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-h-r-1", "field": "field-A"},
                    {"key": "key-h-r-1", "field": "field-B"},
                    {"key": "key-h-r-2", "field": "field-A"},
                    {"key": "key-h-r-2", "field": "field-B"},
                ]
            },
            "cfg": {
                "type": "rsvd",
                "ack": 0 #metto ack 0, ma il demone forza e lo mette a 1, e manda la risposta.
            }
        }

        hget_cmd_rsvd_110 = {
            "C": 7,
            "A": {
                "I": [
                    {"K": "key-h-r-1", "F": "field-A"},
                    {"K": "key-h-r-1", "F": "field-B"},
                    {"K": "key-h-r-2", "F": "field-A"},
                    {"K": "key-h-r-2", "F": "field-B"},
                ]
            },
            "CF": {
                "T": "R",
                "A": 0 #metto ack 0, ma il demone forza e lo mette a 1, e manda la risposta.
            }
        }

        hget_cmd_stng_100 = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-h-s-1", "field": "field-A"},
                    {"key": "key-h-s-1", "field": "field-B"},
                    {"key": "key-h-s-2", "field": "field-A"},
                    {"key": "key-h-s-2", "field": "field-B"},
                ]
            },
            "cfg": {
                "pers": 0,  #imposto la persistenza, ma deve essere scartata in quanto vale il type: stng che prevede pers: 1
                "type": "stng",
                "ack": 1
            }
        }


        hget_cmd_stng_110 = {
            "C": 7,
            "A": {
                "I": [
                    {"K": "key-h-s-1", "F": "field-A"},
                    {"K": "key-h-s-1", "F": "field-B"},
                    {"K": "key-h-s-2", "F": "field-A"},
                    {"K": "key-h-s-2", "F": "field-B"},
                ]
            },
            "CF": {
                "P": 0,  #imposto la persistenza, ma deve essere scartata in quanto vale il type: stng che prevede pers: 1
                "T": "S",
                "A": 1
            }
        }

        hget_cmd_prfx_100 = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-1", "field": "field-A"},
                    {"key": "key-1", "field": "field-B"},
                    {"key": "key-2", "field": "field-A"},
                    {"key": "key-2", "field": "field-B"},
                ]
            },
            "cfg": {
                "pers": 0,
                "type": "appl",
                "prfx": 1,
                "ack": 1
            }
        }

        hget_cmd_prfx_110 = {
            "C": 7,
            "A": {
                "I": [
                    {"K": "key-1", "F": "field-A"},
                    {"K": "key-1", "F": "field-B"},
                    {"K": "key-2", "F": "field-A"},
                    {"K": "key-2", "F": "field-B"},
                ]
            },
            "CF": {
                "P": 0,
                "T": "A",
                "PX": 1,
                "A": 1
            }
        }
        #endregion

        #cmd_list.append(msgpack.packb(hget_cmd_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_pers_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_mix_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_rsvd_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_pers_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_prfx_100, use_bin_type=True))


        #cmd_list.append(msgpack.packb(hget_cmd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_pers_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_mix_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_rsvd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_pers_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_prfx_110, use_bin_type=True))

        #region 8. HDEL
        hdel_cmd_100 = {
            "cmd": "HDEL",
            "args": {
                "items": [
                    {"key": "key-h-1", "field": "field-A"},
                    {"key": "key-h-1", "field": "field-B"},
                    {"key": "key-h-2", "field": "field-A"},
                    {"key": "key-h-2", "field": "field-B"},
                    {"key": "key-h-1", "field": "field-C"}, # non esiste field-C
                    {"key": "key-h-3", "field": "field-A"}, # non esiste key-h-3
                ]
            },
            "cfg": {
                "type": "appl",
                "pers": 0,
                "ack": 1
            }
        }

        hdel_cmd_110 = {
            "C": 8,
            "A": {
                "I": [
                    {"K": "key-h-1", "F": "field-A"},
                    {"K": "key-h-1", "F": "field-B"},
                    {"K": "key-h-2", "F": "field-A"},
                    {"K": "key-h-2", "F": "field-B"},
                    {"K": "key-h-1", "F": "field-C"}, # non esiste field-C
                    {"K": "key-h-3", "F": "field-A"}, # non esiste key-h-3
                ]
            },
            "CF": {
                "T": "A",
                "P": 0,
                "A": 1
            }
        }

        hdel_cmd_pers_100 = {
            "cmd": "HDEL",
            "args": {
                "items": [
                    {"key": "key-h-p-1", "field": "field-A"},
                    {"key": "key-h-p-1", "field": "field-B"},
                    {"key": "key-h-p-2", "field": "field-A"},
                    {"key": "key-h-p-2", "field": "field-B"}
                ]
            },
            "cfg": {
                #"type": "appl", #questa volta commento, perche lo mette in automatico
                "pers": 1,
                "ack": 0
            }
        }

        hdel_cmd_pers_110 = {
            "C": 8,
            "A": {
                "I": [
                    {"K": "key-h-p-1", "F": "field-A"},
                    {"K": "key-h-p-1", "F": "field-B"},
                    {"K": "key-h-p-2", "F": "field-A"},
                    {"K": "key-h-p-2", "F": "field-B"}
                ]
            },
            "CF": {
                #"type": "appl", #questa volta commento, perche lo mette in automatico
                "P": 1,
                "A": 0
            }
        }

        hdel_cmd_prfx_100 = {
            "cmd": "HDEL",
            "args": {
                "items": [
                    {"key": "key-1", "field": "field-A"},
                    {"key": "key-1", "field": "field-B"},
                    {"key": "key-2", "field": "field-A"},
                    {"key": "key-2", "field": "field-B"}
                ]
            },
            "cfg": {
                #"type": "appl", #questa volta commento, perche lo mette in automatico
                "pers": 0,
                "prfx": 1,
                "ack": 0
            }
        }


        hdel_cmd_prfx_110 = {
            "C": 8,
            "A": {
                "I": [
                    {"K": "key-1", "F": "field-A"},
                    {"K": "key-1", "F": "field-B"},
                    {"K": "key-2", "F": "field-A"},
                    {"K": "key-2", "F": "field-B"}
                ]
            },
            "CF": {
                #"type": "appl", #questa volta commento, perche lo mette in automatico
                "P": 0,
                "PX": 1,
                "A": 0
            }
        }
        #endregion
        #cmd_list.append(msgpack.packb(hdel_cmd_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hdel_cmd_pers_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hdel_cmd_prfx_100, use_bin_type=True))

        #cmd_list.append(msgpack.packb(hdel_cmd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hdel_cmd_pers_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hdel_cmd_prfx_110, use_bin_type=True))


        #region 9. PUB

        cmd_pub_100 = {
            "cmd": "PUB",
            "args": {
                "items": [
                    {"channel": "channel-1", "message": "message-A"},
                    {"channel": "channel-2", "message": "message-B"}
                ]
            },
            "cfg": {
                "ack": 1
            }
        }

        cmd_pub_110 = {
            "C": 9,
            "A": {
                "I": [
                    {"C": "channel-1", "M": "message-A"},
                    {"C": "channel-2", "M": "message-B"}
                ]
            },
            "CF": {
                "A": 1
            }
        }

        cmd_pub_prfx_100 = {
            "cmd": "PUB",
            "args": {
                "items": [
                    {"channel": "channel-1", "message": "message-A"},
                    {"channel": "channel-2", "message": "message-B"}
                ]
            },
            "cfg": {
                "ack": 1,
                "prfx": 1
            }
        }

        cmd_pub_prfx_110 = {
            "C": 9,
            "A": {
                "I": [
                    {"C": "channel-1", "M": "message-A"},
                    {"C": "channel-2", "M": "message-B"}
                ]
            },
            "CF": {
                "A": 1,
                "PX": 1
            }
        }
        #endregion

        #cmd_list.append(msgpack.packb(cmd_pub_100, use_bin_type=True))
        #cmd_list.append(msgpack.packb(cmd_pub_prfx_100, use_bin_type=True))

        #cmd_list.append(msgpack.packb(cmd_pub_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(cmd_pub_prfx_110, use_bin_type=True))

        #region 10. FLUSH
        flush_cmd_100 = {
            "cmd": "FLUSH",
            "args": {},
            "cfg": {
                "pers": 0,
                "ack": 1,
            }
        }

        flush_cmd_110 = {
            "C": 10,
            "A": {},
            "CF": {
                "P": 0,
                "A": 1,
            }
        }

        flush_cmd_pers_100 = {
            "cmd": "FLUSH",
            "args": {},
            "cfg": {
                "type": "appl",
                "pers": 1,
                "ack": 1,
            }
        }

        flush_cmd_pers_110 = {
            "C": 10,
            "A": {},
            "CF": {
                "T": "A",
                "P": 1,
                "A": 1,
            }
        }

        # region 12. SUBSCRIBE
        cmd_sub = {
            "cmd": "SUB",
            "args": {
                "items": [
                    "channel-1", "channel-2"
                ]
            },
            "cfg": {
            }
        }
        # endregion

        cmd_list.append(msgpack.packb(cmd_sub, use_bin_type=True))

        #cmd_list.append(msgpack.packb(flush_cmd_110, use_bin_type=True))
        #cmd_list.append(msgpack.packb(flush_cmd_pers_110, use_bin_type=True))

        return cmd_list, rsp_list

    def __service_task(self):
        LOG.info("{} Start Service Task Emulation".format(self.__log_prefix))
        datastore = DATASTORE.getDataStoreStd()
        while not self.__serviceStop.is_set():

            try:
                datastore.publish("{}_HB{}".format(self.__id, "0"), str(int(datetime.now().timestamp() * 1000)))
                time.sleep(0) #cambia il tempo per emulare casi diversi
                datastore.publish("{}_HB{}".format(self.__id, "1"), str(int(datetime.now().timestamp() * 1000)))
                time.sleep(100)
            except Exception as ex:
                print(ex)

            #region HEARTBEAT
