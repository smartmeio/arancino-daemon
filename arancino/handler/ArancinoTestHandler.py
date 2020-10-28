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
from arancino.utils.ArancinoUtils import *
from arancino.port.ArancinoPort import PortTypes
from arancino.ArancinoCortex import ArancinoCommandIdentifiers as cmdId
from arancino.ArancinoConstants import ArancinoSpecialChars as specChars
from arancino.ArancinoConstants import ArancinoCommandResponseCodes as respCodes
from arancino.ArancinoConstants import ArancinoCommandErrorCodes as errorCodes
import time

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()

class ArancinoTestHandler(threading.Thread):

    def __init__(self, name, id, device, commandReceivedHandler, connectionLostHandler):
        threading.Thread.__init__(self, name=name)

        self.__name = name          # the name, usually the arancino port id
        self.__id = id
        self.__device = device
        self.__log_prefix = "[{} - {} at {}]".format(PortTypes(PortTypes.TEST).name, self.__id, self.__device)

        self.__commandReceivedHandler = commandReceivedHandler  # handler to be called when a raw command is complete and ready to be translated and executed.
        self.__connectionLostHandler = connectionLostHandler    # handler to be called when a connection is lost or stopped

        self.__command_delay = CONF.get_port_test_delay()

        self.__stop = False

        self.__command_test_list = self.__getCommnandsList()
        self.__command_test_del_list = self.__getCommnandsDelList()

    def run(self):
        time.sleep(1.5) # do il tempo ad Arancino di inserire la porta in lista
        commands_test_num = len(self.__command_test_list)
        count = 0

        if commands_test_num > 0:
            while not self.__stop:
                # Ricezione dati
                try:


                    raw_cmd = self.__command_test_list[count]

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

    def __getCommnandsDelList(self):

        ### keys used:
        # <ID>_TEST_KEY
        # <ID>_TEST_PERS_KEY
        # <ID>_TEST_HSET
        list = []
        # DEL
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_PERS_KEY" + specChars.CHR_EOT)
        # HDEL
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_3" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_4" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_5" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_6" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_7" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_8" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_9" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_10" + specChars.CHR_EOT)
        # DEL
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET_PERS" + specChars.CHR_EOT)


        # DEL
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_2" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_3" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_1" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_2" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_3" + specChars.CHR_EOT)

        return list

    def __getCommnandsList(self):

        ### keys used:
        # <ID>_TEST_KEY
        # <ID>_TEST_PERS_KEY
        # <ID>_TEST_HSET

        list = []

        # START
            # firmware upload date time
        fw_date_str = "Oct 21 1988"
        fw_time_str = "12:48:00"
        fw_tz_str = "+0600"
        fw_datetime_str = fw_date_str + ' ' + fw_time_str + ' ' + fw_tz_str
        #fw_datetime_str = ""
            # firmware version
        fw_version = "0.0.1"
        #fw_version = ""

            # fimware name
        fw_name = "Arancino Test Port Firmware"
        #fw_name = ""
            # arancino library version

        lib_version = "1.0.0"
        core_version = "1.0.0"

        # 1. START
        list.append(cmdId.CMD_SYS_START["id"] + specChars.CHR_SEP + lib_version + specChars.CHR_SEP + fw_name + specChars.CHR_SEP + fw_version + specChars.CHR_SEP + fw_datetime_str + specChars.CHR_SEP + core_version + specChars.CHR_EOT)
        #list.append(cmdId.CMD_SYS_START["id"] + specChars.CHR_SEP + lib_version + specChars.CHR_EOT)
        
        # 2. SET
        list.append(cmdId.CMD_APP_SET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY" + specChars.CHR_SEP + "TEST_VAL" + specChars.CHR_EOT)

        # 3. SET PERSISTENT
        list.append(cmdId.CMD_APP_SET_PERS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_PERS_KEY" + specChars.CHR_SEP + "TEST_PERS_VAL" + specChars.CHR_EOT)

        # 4. GET
            # 4.1 OK
        list.append(cmdId.CMD_APP_GET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY" + specChars.CHR_EOT)

            # 4.2 KO
        list.append(cmdId.CMD_APP_GET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY_DOES_NOT_EXIST" + specChars.CHR_EOT)

            # 4.3 GET of a persistent key
        list.append(cmdId.CMD_APP_GET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_PERS_KEY" + specChars.CHR_EOT)

        # 5. KEYS
            # 5.1 w/ wildcard
        list.append(cmdId.CMD_APP_KEYS["id"] + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 5.2 w/ specified name and wildcard
        list.append(cmdId.CMD_APP_KEYS["id"] + specChars.CHR_SEP + "TEST*" + specChars.CHR_EOT)

        # 6. DEL
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY" + specChars.CHR_EOT)

        # 7. HSET
        list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_SEP + "TEST_VAL_1" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_SEP + "TEST_VAL_2" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_3" + specChars.CHR_SEP + "TEST_VAL_3" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_4" + specChars.CHR_SEP + "TEST_VAL_4" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_5" + specChars.CHR_SEP + "TEST_VAL_5" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_6" + specChars.CHR_SEP + "TEST_VAL_6" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_7" + specChars.CHR_SEP + "TEST_VAL_7" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_8" + specChars.CHR_SEP + "TEST_VAL_8" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_9" + specChars.CHR_SEP + "TEST_VAL_9" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_SEP + "TEST_VAL_10" + specChars.CHR_EOT)

            # 7.2 HSET PERS OK
        #list.append(cmdId.CMD_APP_HSET_PERS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET_PERS" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_SEP + "TEST_VAL_1" + specChars.CHR_EOT)
        #list.append(cmdId.CMD_APP_HSET_PERS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET_PERS" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_SEP + "TEST_VAL_2" + specChars.CHR_EOT)

            # 7.3 HSET PERS KO -> keys exists in volatile dastatore
        list.append(cmdId.CMD_APP_HSET_PERS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_SEP + "TEST_VAL_1" + specChars.CHR_EOT)



        # HGET
            # 8.1 HGET OK
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_3" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_4" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_5" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_6" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_7" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_8" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_9" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_10" + specChars.CHR_EOT)

            # 8.2 HGET HGET OF a key/field that doesn't exist
        list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET_DOES_NOT_EXIST" + specChars.CHR_SEP + "TEST_FIELD_DOES_NOT_EXIST" + specChars.CHR_EOT)
        
        # 9. HGETALL
        list.append(cmdId.CMD_APP_HGETALL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)
        
        # 10. HVALS
        list.append(cmdId.CMD_APP_HVALS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)
        
        # 11. HKEYS
        list.append(cmdId.CMD_APP_HKEYS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)
        
        # 12. HDEL
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_3" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_4" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_5" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_6" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_7" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_8" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_9" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_HDEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_10" + specChars.CHR_EOT)
        # DEL
        list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)

        # 13. PUB
        list.append(cmdId.CMD_APP_PUB["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_PUB" + specChars.CHR_SEP + "TEST_PUB_VAL" + specChars.CHR_EOT)
       
        # 14. MSET
            # 14.1 MSET STD OK
        keys = str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_2" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_3"
        values = "TEST_MSET_VAL_1" + specChars.CHR_ARR_SEP + "TEST_MSET_VAL_2" + specChars.CHR_ARR_SEP + "TEST_MSET_VAL_3"
        list.append(cmdId.CMD_APP_MSET_STD["id"] + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)

            # 14.2 MSET STD KO
        #keys = str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_2"
        #list.append(cmdId.CMD_APP_MSET_STD["id"] + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)

            # 14.3 MSET PERS
        # keys = str(self.__id) + "_TEST_MSET_KEY_PERS_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_2" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_PERS_3"
        # values = "TEST_MSET_VAL_1" + specChars.CHR_ARR_SEP + "TEST_MSET_VAL_2" + specChars.CHR_ARR_SEP + "TEST_MSET_VAL_3"
        # list.append(cmdId.CMD_APP_MSET_PERS["id"] + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)

            # 14.4 MSET PERS KO - keys exists in standard datastore
        keys = str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_2" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MSET_KEY_3"
        list.append(cmdId.CMD_APP_MSET_PERS["id"] + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)


        
        # 15. MGET
            # 15.1 OK
        list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)
        
            # 15.2 KO -> key does not exist
        keys = str(self.__id) + "_TEST_MGET_1"
        list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)

            # 15.3 KO -> keys don't exist
        keys = str(self.__id) + "_TEST_MGET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MGET_KEY_2"
        list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)

            # 15.4 KO -> one key does not exist
        keys = str(self.__id) + "_TEST_MSET_KEY_1" + specChars.CHR_ARR_SEP + str(self.__id) + "_TEST_MGET_KEY_2"
        list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)

            # 15.5 KO -> empty list
        keys = ""
        list.append(cmdId.CMD_APP_MGET["id"] + specChars.CHR_SEP + keys + specChars.CHR_EOT)


        return list

