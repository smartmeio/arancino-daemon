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
import time

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
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

        ### keys used:
        # <ID>_TEST_KEY
        # <ID>_TEST_PERS_KEY
        # <ID>_TEST_HSET

        cmd_list = []
        rsp_list = []

        # region 1. START
        # firmware upload date time
        fw_date_str = "Oct 21 1985"
        fw_time_str = "09:00:00"
        fw_tz_str = "+0600"
        fw_datetime_str = fw_date_str + ' ' + fw_time_str + ' ' + fw_tz_str

        start_cmd = {
            "cmd": "START",
            "args": {
                "port_id": "TEST_36663",#"TEST_{}".format(random.randint(10000, 99999)),
                "fw_mcu_family": "Test Family",
                "fw_lib_ver": "3.0.0",
                "fw_name": "My Awesome Firmware",
                "fw_ver": "1.0.0",
                "fw_build_time": fw_datetime_str,
                "fw_core_ver": "1.0.0",
                "fw_crtx_ver": "1.0.0",
                "CUSTOM_KEY_1": "CUSTOM_VALUE_1",
                "CUSTOM_KEY_2": "CUSTOM_VALUE_2"
            },
            "cfg": {
                "scr_mod": 0
            }
        }

        start_rsp = {
            "code": ArancinoCommandResponseCodes.RSP_OK,
            "args": {
                "dmn_ver" : str(CONF.get_metadata_version()),
                "dmn_env": CONF.get_general_env()
            },
            "cfg": {
                #"ts": "<timestamp>",
                "log_lvl": CONF.get("log").get("level")
            }
        }
        # endregion

        cmd_list.append(msgpack.packb(start_cmd, use_bin_type=True))
        rsp_list.append(msgpack.packb(start_rsp, use_bin_type=True))



        #region 2. SET
        set_cmd_appl = {
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

        set_cmd_appl_pers = {
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

        set_cmd_rsvd = {
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

        set_cmd_stng = {
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
        #endregion
        #cmd_list.append(msgpack.packb(set_cmd_appl, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_appl_pers, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_rsvd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(set_cmd_stng, use_bin_type=True))

        #region 3. GET

        get_cmd = {
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

        get_cmd_pers = {
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

        get_cmd_mix = {
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

        get_cmd_rsvd = {
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

        get_cmd_stng = {
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
        # endregion

        #cmd_list.append(msgpack.packb(get_cmd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_pers, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_mix, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_rsvd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(get_cmd_pers, use_bin_type=True))


        #region 4. DEL
        del_cmd = {
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

        del_cmd_pers = {
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
        #endregion
        #cmd_list.append(msgpack.packb(del_cmd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(del_cmd_pers, use_bin_type=True))


        #region 5. HSET
        hset_cmd_appl = {
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

        hset_cmd_appl_pers = {
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

        hset_cmd_rsvd = {
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

        hset_cmd_stng = {
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
        #endregion

        #cmd_list.append(msgpack.packb(hset_cmd_appl, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_appl_pers, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_rsvd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hset_cmd_stng, use_bin_type=True))


        #region 6. HGET
        hget_cmd = {
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

        hget_cmd_pers = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-p-1", "field": "field-A"},
                    {"key": "key-p-1", "field": "field-B"},
                    {"key": "key-p-2", "field": "field-A"},
                    {"key": "key-p-2", "field": "field-B"},
                ]
            },
            "cfg": {
                "pers": 1,
                "type": "appl"
            }
        }

        hget_cmd_mix = {
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

        hget_cmd_rsvd = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-r-1", "field": "field-A"},
                    {"key": "key-r-1", "field": "field-B"},
                    {"key": "key-r-2", "field": "field-A"},
                    {"key": "key-r-2", "field": "field-B"},
                ]
            },
            "cfg": {
                "type": "rsvd",
                "ack": 0 #metto ack 0, ma il demone forza e lo mette a 1, e manda la risposta.
            }
        }

        hget_cmd_stng = {
            "cmd": "HGET",
            "args": {
                "items": [
                    {"key": "key-s-1", "field": "field-A"},
                    {"key": "key-s-1", "field": "field-B"},
                    {"key": "key-s-2", "field": "field-A"},
                    {"key": "key-s-2", "field": "field-B"},
                ]
            },
            "cfg": {
                "pers": 0,  #imposto la persistenza, ma deve essere scartata in quanto vale il type: stng che prevede pers: 1
                "type": "stng",
                "ack": 1
            }
        }
        #endregion

        #cmd_list.append(msgpack.packb(hget_cmd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_pers, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_mix, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_rsvd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hget_cmd_pers, use_bin_type=True))

        #region 7. HDEL
        hdel_cmd = {
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

        hdel_cmd_pers = {
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

        #endregion
        #cmd_list.append(msgpack.packb(hdel_cmd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(hdel_cmd_pers, use_bin_type=True))

        #region 8. FLUSH
        flush_cmd = {
            "cmd": "FLUSH",
            "args": {},
            "cfg": {
                "pers": 0,
                "ack": 1,
            }
        }

        flush_cmd_pers = {
            "cmd": "FLUSH",
            "args": {},
            "cfg": {
                "type": "appl",
                "pers": 1,
                "ack": 1,
            }
        }

        #endregion
        #cmd_list.append(msgpack.packb(flush_cmd, use_bin_type=True))
        #cmd_list.append(msgpack.packb(flush_cmd_pers, use_bin_type=True))


        #region 9. PUB

        #endregion


        #region 10. STORE
        cmd_store = {
            "cmd": "STORE",
            "args": {
                "items": [
                    {"key": "key-1", "value": 1, "ts": "*"},
                    {"key": "key-2", "value": 2, "ts": "*"},
                    {"key": "key-3", "value": 3.14},
                ]
            },
            "cfg": {
                "ack": 1
            }
        }
        #endregion

        #cmd_list.append(msgpack.packb(cmd_store, use_bin_type=True))

        # region 11. STORETAGS
        cmd_store_tag = {
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

            }
        }
        # endregion
        #cmd_list.append(msgpack.packb(cmd_store_tag, use_bin_type=True))

        #region 12. PUB

        cmd_pub = {
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

        #endregion

        cmd_list.append(msgpack.packb(cmd_pub, use_bin_type=True))

        # # 13. PUB
        # list.append(cmdId.CMD_APP_PUB["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_PUB" + specChars.CHR_SEP + "TEST_PUB_VAL" + specChars.CHR_EOT)
        #
        # # 14. MSET
        #     # 14.1 MSET STD OK
        # keys = str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_2" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_3"
        # values = "TEST_MSET_VAL_1" + specChars.CHR_ARR_SEP + "TEST_MSET_VAL_2" + specChars.CHR_ARR_SEP + "TEST_MSET_VAL_3"
        # list.append(cmdId.CMD_APP_MSET_STD["id"] + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)
        #
        #     # 14.2 MSET STD KO
        # keys = str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_2"
        # list.append(cmdId.CMD_APP_MSET_STD["id"] + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)
        #
        #     # 14.3 MSET PERS
        # keys = str(self.__id) + "_TEST_MSET_KEY_PERS_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_2" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_3"
        # values = "TEST_MSET_VAL_1" + specChars.CHR_ARR_SEP + "TEST_MSET_VAL_2" + specChars.CHR_ARR_SEP + "TEST_MSET_VAL_3"
        # list.append(cmdId.CMD_APP_MSET_PERS["id"] + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)
        #
        #     # 14.4 MSET PERS KO - keys exists in standard datastore
        # keys = str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_2" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_3"
        # list.append(cmdId.CMD_APP_MSET_PERS["id"] + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)
        #
        #
        #
        # # 15. MGET
        #     # 15.1 OK
        # list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)
        #
        #     # 15.2 KO -> key does not exist
        # keys = str(self.__id) + "_TEST_MGET_1"
        # list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)
        #
        #     # 15.3 KO -> keys don't exist
        # keys = str(self.__id) + "_TEST_MGET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MGET_KEY_2"
        # list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)
        #
        #     # 15.4 KO -> one key does not exist
        # keys = str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MGET_KEY_2"
        # list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)
        #
        #     # 15.5 KO -> empty list
        # keys = ""
        # list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)

        # 16. STORE
            # 16.1 OK
        #list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1" + specChars.CHR_SEP + "1" +specChars.CHR_EOT)

            # 16.2 OK
        #list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1" + specChars.CHR_SEP + "1.1" + specChars.CHR_EOT)

            # 16.3 KO
        #list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1" + specChars.CHR_SEP + "1A" + specChars.CHR_EOT)

            # 16.4 OK
        """
        keys = "TAG_1" + specChars.CHR_ARR_SEP + "TAG_2" + specChars.CHR_ARR_SEP + "TAG_3"
        values = "VAL_1" + specChars.CHR_ARR_SEP + "VAL_2" + specChars.CHR_ARR_SEP + "VAL_3"

        #list.append(cmdId.CMD_APP_STORETAGS["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)

        # list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "1" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

        #     # 16.5 OK
        # list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "2" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

        #     # 16.6 KO
        # list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "3" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

        #     # 16.7 KO
        # list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "4" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.8 KO
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "1" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "2" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "3" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "4" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        keys = "TAG_1" + specChars.CHR_ARR_SEP + "TAG_2" + specChars.CHR_ARR_SEP + "TAG_3"
        values = "VAL_1-1" + specChars.CHR_ARR_SEP + "VAL_2-1" + specChars.CHR_ARR_SEP + "VAL_3-1"

        #list.append(cmdId.CMD_APP_STORETAGS["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)


        # list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "1" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

        #     # 16.5 OK
        # list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "2" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

        #     # 16.6 KO
        # list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "3" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

        #     # 16.7 KO
        # list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "4" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.8 KO
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "1" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "2" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "3" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "4" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        """
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
