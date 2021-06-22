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
from arancino.ArancinoCortex import ArancinoComamnd, ArancinoCommandIdentifiers as cmdId
from arancino.ArancinoConstants import ArancinoCommandIdentifiers, ArancinoSpecialChars as specChars, ArancinoPortAttributes
from arancino.ArancinoConstants import ArancinoCommandResponseCodes as respCodes
from arancino.ArancinoConstants import ArancinoCommandErrorCodes as errorCodes
from arancino.ArancinoConstants import SUFFIX_TMSTP
import time

#import for asimmetric authentication
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import datetime
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from base64 import b64decode


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

        #load certificates from files
        self.__signer_cert = self.__retrieve_signer_cert()
        self.__device_cert = self.__retrive_device_cert()
        self.challenge = None
        
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
                    acmd = ArancinoComamnd(raw_command=raw_cmd)
                    if acmd.getId() != ArancinoCommandIdentifiers.CMD_SYS_START["id"]:
                        #crea e aggiungi firma
                        signature = self.__signChallenge(self.challenge)
                        acmd = self.addSign(acmd, signature)
                        LOG.debug("Siamo nel test handler: Signature = {} | Comamnd = {}".format(str(signature), acmd.getRaw()))

                    # send back the raw command
                    if self.__commandReceivedHandler is not None:
                        response = self.__commandReceivedHandler(raw_cmd)
                        self.challenge = response.retrieveChallenge()

                    if acmd.getId() == ArancinoCommandIdentifiers.CMD_SYS_START["id"]:
                        self.addSignCommand()
                        count = 0

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
                
                # Ricezione dati
                self.__consumeResponse(acmd, response)
                LOG.debug("{} Response received: {}: {}".format(self.__log_prefix, response.getId(), str(response.getArguments())))

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

        list = []

        # START
            # firmware upload date time
        fw_date_str = "Oct 21 1985"
        fw_time_str = "09:00:00"
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

        lib_version = "1.2.0"
        core_version = "1.0.0"

            # micro controller family
        micro_family = "Test Family"

            # generic attributes
        custom_attrib_key_1 = "CUSTOM1"
        custom_attrib_val_1 = "foo"

        custom_attrib_key_2 = "CUSTOM2"
        custom_attrib_val_2 = "bar"

            #asimmetric authentication attributes
        signer_cert_key = "SIGNER_CERT"
        signer_cert_val = self.__retrieve_signer_cert()

        device_cert_key = "DEVICE_CERT"
        device_cert_val = self.__retrive_device_cert()

        start_args_keys_array = [ArancinoPortAttributes.FIRMWARE_LIBRARY_VERSION,
                                 ArancinoPortAttributes.FIRMWARE_BUILD_TIME,
                                 ArancinoPortAttributes.FIRMWARE_CORE_VERSION,
                                 ArancinoPortAttributes.FIRMWARE_NAME,
                                 ArancinoPortAttributes.MCU_FAMILY,
                                 ArancinoPortAttributes.FIRMWARE_VERSION,
                                 signer_cert_key,
                                 device_cert_key,
                                 custom_attrib_key_1,
                                 custom_attrib_key_2
                                 ]

        start_args_vals_array = [lib_version,
                                 fw_datetime_str,
                                 core_version,
                                 fw_name,
                                 micro_family,
                                 fw_version,
                                 str(signer_cert_val.public_bytes(
                                     encoding=serialization.Encoding.PEM)),
                                 str(device_cert_val.public_bytes(
                                     encoding=serialization.Encoding.PEM)),
                                 custom_attrib_val_1,
                                 custom_attrib_val_2]

        start_args_keys = specChars.CHR_ARR_SEP.join(start_args_keys_array)
        start_args_vals = specChars.CHR_ARR_SEP.join(start_args_vals_array)

        # 1. START
        # list.append(cmdId.CMD_SYS_START["id"] + specChars.CHR_SEP + lib_version + specChars.CHR_EOT)
        # list.append(cmdId.CMD_SYS_START["id"] + specChars.CHR_SEP + lib_version + specChars.CHR_SEP + fw_name + specChars.CHR_SEP + fw_version + specChars.CHR_SEP + fw_datetime_str + specChars.CHR_SEP + core_version + specChars.CHR_EOT)
        list.append(cmdId.CMD_SYS_START["id"] + specChars.CHR_SEP + start_args_keys + specChars.CHR_SEP + start_args_vals + specChars.CHR_EOT)
        
        # # 2. SET
        # list.append(cmdId.CMD_APP_SET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY" + specChars.CHR_SEP + "TEST_VAL" + specChars.CHR_EOT)
        #
        # # 3. SET PERSISTENT
        # list.append(cmdId.CMD_APP_SET_PERS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_PERS_KEY" + specChars.CHR_SEP + "TEST_PERS_VAL" + specChars.CHR_EOT)
        #
        # # 4. GET
        #     # 4.1 OK
        # list.append(cmdId.CMD_APP_GET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY" + specChars.CHR_EOT)
        #
        #     # 4.2 KO
        # list.append(cmdId.CMD_APP_GET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY_DOES_NOT_EXIST" + specChars.CHR_EOT)
        #
        #     # 4.3 GET of a persistent key
        # list.append(cmdId.CMD_APP_GET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_PERS_KEY" + specChars.CHR_EOT)
        #
        # # 5. KEYS
        #     # 5.1 w/ wildcard
        # list.append(cmdId.CMD_APP_KEYS["id"] + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        #
        #     # 5.2 w/ specified name and wildcard
        # list.append(cmdId.CMD_APP_KEYS["id"] + specChars.CHR_SEP + "TEST*" + specChars.CHR_EOT)
        #
        # # 6. DEL
        # list.append(cmdId.CMD_APP_DEL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_KEY" + specChars.CHR_EOT)
        #
        # # 7. HSET
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_SEP + "TEST_VAL_1" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_SEP + "TEST_VAL_2" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_3" + specChars.CHR_SEP + "TEST_VAL_3" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_4" + specChars.CHR_SEP + "TEST_VAL_4" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_5" + specChars.CHR_SEP + "TEST_VAL_5" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_6" + specChars.CHR_SEP + "TEST_VAL_6" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_7" + specChars.CHR_SEP + "TEST_VAL_7" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_8" + specChars.CHR_SEP + "TEST_VAL_8" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_9" + specChars.CHR_SEP + "TEST_VAL_9" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_STD["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_SEP + "TEST_VAL_10" + specChars.CHR_EOT)
        #
        #     # 7.2 HSET PERS OK
        # list.append(cmdId.CMD_APP_HSET_PERS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET_PERS" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_SEP + "TEST_VAL_1" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HSET_PERS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET_PERS" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_SEP + "TEST_VAL_2" + specChars.CHR_EOT)
        #
        #     # 7.3 HSET PERS KO -> keys exists in volatile dastatore
        # list.append(cmdId.CMD_APP_HSET_PERS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_SEP + "TEST_VAL_1" + specChars.CHR_EOT)
        #
        # # HGET
        #     # 8.1 HGET OK
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_1" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_2" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_3" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_4" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_5" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_6" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_7" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_8" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_9" + specChars.CHR_EOT)
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_SEP + "TEST_FIELD_10" + specChars.CHR_EOT)
        #
        #     # 8.2 HGET HGET OF a key/field that doesn't exist
        # list.append(cmdId.CMD_APP_HGET["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET_DOES_NOT_EXIST" + specChars.CHR_SEP + "TEST_FIELD_DOES_NOT_EXIST" + specChars.CHR_EOT)
        #
        # # 9. HGETALL
        # list.append(cmdId.CMD_APP_HGETALL["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)
        #
        # # 10. HVALS
        # list.append(cmdId.CMD_APP_HVALS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)
        #
        # # 11. HKEYS
        # list.append(cmdId.CMD_APP_HKEYS["id"] + specChars.CHR_SEP + str(self.__id) + "_TEST_HSET" + specChars.CHR_EOT)
        #
        # # 12. HDEL
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
        #
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
        '''
        keys = "TAG_1" + specChars.CHR_ARR_SEP + "TAG_2" + specChars.CHR_ARR_SEP + "TAG_3"
        values = "VAL_1" + specChars.CHR_ARR_SEP + "VAL_2" + specChars.CHR_ARR_SEP + "VAL_3"

        list.append(cmdId.CMD_APP_STORETAGS["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)

        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "1" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.5 OK
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "2" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.6 KO
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "3" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.7 KO
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "4" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.8 KO
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "1" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "2" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "3" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "4" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

        keys = "TAG_1" + specChars.CHR_ARR_SEP + "TAG_2" + specChars.CHR_ARR_SEP + "TAG_3"
        values = "VAL_1-1" + specChars.CHR_ARR_SEP + "VAL_2-1" + specChars.CHR_ARR_SEP + "VAL_3-1"

        list.append(cmdId.CMD_APP_STORETAGS["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + keys + specChars.CHR_SEP + values + specChars.CHR_EOT)


        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "1" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.5 OK
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "2" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.6 KO
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "3" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.7 KO
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_1/value/0" + specChars.CHR_SEP + "4" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)

            # 16.8 KO
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "1" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "2" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "3" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        list.append(cmdId.CMD_APP_STORE["id"] + specChars.CHR_SEP + str(self.__id) + "_TS_2/value/0" + specChars.CHR_SEP + "4" + specChars.CHR_SEP + "*" + specChars.CHR_EOT)
        '''
        return list

    def __retrieve_signer_cert(self):
        cur_path = os.path.dirname(__file__)
        cur_path = cur_path[:-16]
        add_path = 'extras/certificates/signerCert.pem'
        new_path = cur_path + add_path
        file_signer_cert = open(new_path, "rb")
        signer_data_cert = file_signer_cert.read()
        return x509.load_pem_x509_certificate(signer_data_cert)

    def __retrive_device_cert(self):
        cur_path = os.path.dirname(__file__)
        cur_path = cur_path[:-16]
        add_path = 'extras/certificates/deviceCert.pem'
        new_path = cur_path + add_path
        file_device_cert = open(new_path, "rb")
        device_data_cert = file_device_cert.read()
        return x509.load_pem_x509_certificate(device_data_cert)

    def getPrivateKey(self):
        return ec.derive_private_key(
            2, ec.SECP384R1(), default_backend())

    def addSign(self, acmd, signature):
        args = acmd.getArguments()
        keys = args[0]
        values = args[1]

        keys_array = keys.split(specChars.CHR_ARR_SEP)
        values_array = values.split(specChars.CHR_ARR_SEP)

        start_args_keys = specChars.CHR_ARR_SEP.join(keys_array)
        start_args_vals = specChars.CHR_ARR_SEP.join(values_array)

        keys_array.append("sign")
        values_array.append(str(signature))
        command = acmd.getId() + specChars.CHR_SEP + start_args_keys + specChars.CHR_SEP + start_args_vals + specChars.CHR_EOT
        LOG.debug("Add sign to command: "+ command)
        acmd = ArancinoComamnd(raw_command=command)
        return acmd

        
    def addSignCommand(self):
        signature = self.__signChallenge(self.challenge)
        signCommand = cmdId.CMD_SYS_SIGN["id"] + specChars.CHR_SEP + "sign" + specChars.CHR_SEP + str(signature) + specChars.CHR_EOT
        self.__command_test_list[0] = signCommand
        LOG.debug("Add SIGN command to TestHandler: "+ signCommand)

    def __consumeResponse(self, arcm, arsp):
        #If response to START COMMAND is the challenge (policy) then sign it and send another command with the signed challenge in itself
        LOG.debug("Response to consume: " + str(arcm.getId()))
        if arcm.getId() == cmdId.CMD_SYS_START:
            self.__signChallenge(self.challenge)

        #other command for consume response not defined, so they need to be implement if it's usefull

    # get challenge from response and sign it

    def __signChallenge(self, challenge):
        data = b64decode(challenge)
        LOG.debug("data = "+str(data))
        return self.getPrivateKey().sign(data, ec.ECDSA(hashes.SHA256()))

    def __addSignToCommand(self, command):
        pass
