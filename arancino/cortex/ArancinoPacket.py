# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2022 SmartMe.IO

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

from abc import ABC, abstractmethod
from arancino.ArancinoConstants import ArancinoCommandErrorCodes
from arancino.ArancinoExceptions import InvalidCommandException
import msgpack


class ArancinoPacket(ABC):
    """
    Usato per Arancino Command e Arancino Response, perche hanno la stessa struttura di base,
        si differenziano solo per "cmd" (Arancino Command) e "rsp_code" (Arancino Response)
    """

    def __init__(self, packet: dict):

        self._packed_packet = None
        self._unpacked_packet = None

        if packet:

            self.args = packet[PCK.PACKET[self.cortex_version].ARGUMENT]
            self.cfg = packet[PCK.PACKET[self.cortex_version].CONFIGURATION]

        else:

            self.args = {}
            self.cfg = {}


    @property
    def cfg(self):
        return self.__cfg


    @cfg.setter
    def cfg(self, cfg: dict):
        self.__cfg = cfg


    @property
    def args(self):
        return self.__args


    @args.setter
    def args(self, args: dict):
        self.__args = args


    @abstractmethod
    def _create_packet(self):
        pass


    def getUnpackedPacket(self):

        pck = self._create_packet()
        return pck


    def getPackedPacket(self):

        pck = self._create_packet()
        packed_pck = msgpack.packb(pck, use_bin_type=True)
        return packed_pck


    @property
    def cortex_version(self):
        return self.__cortex_version

    @cortex_version.setter
    def cortex_version(self, cortex_version: str):
        self.__cortex_version = cortex_version


class ArancinoCommand(ArancinoPacket):

    def __init__(self, packet):

        if packet:

            if isinstance(packet, dict):

                self.__set_cortex_version_by_packet(packet)
                self.id = packet[PCK.PACKET[self.cortex_version].CMD.COMMAND_ID]

            elif isinstance(packet, bytes):

                # trasformo packet in dict
                packet = msgpack.unpackb(packet, use_list=True, raw=False)
                self.__set_cortex_version_by_packet(packet)
                self.id = packet[PCK.PACKET[self.cortex_version].CMD.COMMAND_ID]

            else:

                # Tipo non riconosciuto/accettato
                raise InvalidCommandException("Invalid Command type/format - Skipped", ArancinoCommandErrorCodes.ERR_CMD_TYPE)


        else:

            self.id = None

        super().__init__(packet=packet)


    @property
    def id(self):
        return self.__cmd_id

    @id.setter
    def id(self, cmd_id: str):
        self.__cmd_id = cmd_id


    def _create_packet(self):

        pck = {}
        pck.update({PCK.PACKET[self.cortex_version].CMD.COMMAND_ID: self.id})
        pck.update({PCK.PACKET[self.cortex_version].CONFIGURATION: self.cfg})
        pck.update({PCK.PACKET[self.cortex_version].ARGUMENT: self.args})

        return pck

    def __set_cortex_version_by_packet(self, packet):
        # Versione 1.0.0: CMD : "cmd"
        if "cmd" in packet:
            self.cortex_version = "1.0.0"
        # Versione 1.1.0: CMD : "C"
        elif "C" in packet:
            self.cortex_version = "1.1.0"
        else:
            # Tipo non riconosciuto/accettato
            raise InvalidCommandException("Invalid Cortex Version - Skipped", ArancinoCommandErrorCodes.ERR_CMD_TYPE)


class ArancinoResponse(ArancinoPacket):

    def __init__(self, packet, cortex_version):

        self.cortex_version = cortex_version

        if packet:

            if isinstance(packet, dict):

                #self.code = packet[PACKET.RSP.RESPONSE_CODE]
                self.code = packet[PCK.PACKET[self.cortex_version].RSP.RESPONSE_CODE]

            elif isinstance(packet, bytes):

                # trasformo packet in dict
                packet = msgpack.unpackb(packet, use_list=True, raw=False)
                #self.code = packet[PACKET.RSP.RESPONSE_CODE]
                self.code = packet[PCK.PACKET[self.cortex_version].RSP.RESPONSE_CODE]

            else:

                # Tipo non riconosciuto/accettato
                raise InvalidCommandException("Invalid Command type/format - Skipped", ArancinoCommandErrorCodes.ERR_CMD_TYPE)


        else:

            self.code = None

        super().__init__(packet=packet)

    @property
    def code(self):
        return self.__response_code

    @code.setter
    def code(self, response_code: int):
        self.__response_code = response_code


    def _create_packet(self):

        pck = {}
        """
        pck.update({PACKET.RSP.RESPONSE_CODE: self.code})
        pck.update({PACKET.CONFIGURATION: self.cfg})
        pck.update({PACKET.ARGUMENT: self.args})
        """
        pck.update({PCK.PACKET[self.cortex_version].RSP.RESPONSE_CODE: self.code})
        pck.update({PCK.PACKET[self.cortex_version].CONFIGURATION: self.cfg})
        pck.update({PCK.PACKET[self.cortex_version].ARGUMENT: self.args})

        return pck


class PACKET_110:
    """
    Version 1.1.0 of Cortex Protocol keys
    """


    CONFIGURATION = "CF"
    ARGUMENT = "A"

    class CMD:

        COMMAND_ID = "C"

        class CMDS:
            START = 0
            SET = 1
            GET = 2
            DEL = 3
            STORE = 4
            STORETAGS = 5
            HSET = 6
            HGET = 7
            HDEL = 8
            PUB = 9
            FLUSH = 10
            SIGN = 11

        class ARGUMENTS:

            ITEMS = "I"
            KEYS = "K"
            PORT_ID = "P"
            PORT_TYPE = "PT"

            TIMESTAMP = "TS"

            class ITEM:
                KEY = "K"
                VALUE = "V"
                FIELD = "F"
                TIMESTAMP = "TS"
                TAG = "N"
                CHANNEL = "C"
                MESSAGE = "M"

            class FIRMWARE:

                MCU_FAMILY = "FMF"
                LIBRARY_VERSION = "FLV"
                NAME = "FN"
                VERSION = "FV"
                BUILD_TIME = "FBT"
                CORE_VERSION = "FCV"
                CORTEX_VERSION = "FXV"
                USE_FREERTOS = "FFOS"

        class CONFIGURATIONS:
            SECURE_MODE = "SM"
            SIGNER_CERTIFICATE = "CS"
            DEVICE_CERTIFICATE = "DS"

            SIGNATURE = "SGN"

            PERSISTENT = "P"
            ACKNOLEDGEMENT = "A"
            PREFIX_ID = "PX"

            TYPE = "T"

            class TYPES:

                APPLICATION = "A"
                SETTING = "S"
                RESERVED = "R"

                TIMESERIES = "TS"
                TSTAGS = "TT"


    class RSP:

        RESPONSE_CODE = "RC"

        class RSPS:

            _100: 100
            _101: 101
            _102: 102
            _200: 200
            _201: 201
            _202: 202
            _203: 203
            _204: 204
            _205: 205
            _206: 206
            _207: 207
            _208: 208
            _209: 209
            _210: 210


        class ARGUMENTS:

            DAEMON_VERSION = "DV"
            DAEMON_ENVIRONMENT = "DE"

            ITEMS = "I"
            KEYS = "K"

            CLIENTS = "C"


        class CONFIGURATIONS:

            CHALLENGE = "CLG"

            TIMESTAMP = "TS"
            LOG_LEVEL = "LL"


class PACKET_100:
    """
    Version 1.0.0 of Cortex Protocol keys
    """


    CONFIGURATION = "cfg"
    ARGUMENT = "args"

    class CMD:

        COMMAND_ID = "cmd"

        class CMDS:

            START = "START"
            SET = "SET"
            GET = "GET"
            DEL = "DEL"
            STORE = "STORE"
            STORETAGS = "STORETAGS"
            HSET = "HSET"
            HGET = "HGET"
            HDEL = "HDEL"
            PUB = "PUB"
            FLUSH = "FLUSH"
            SIGN = "SIGN"

        class ARGUMENTS:

            ITEMS = "items"
            KEYS = "keys"
            PORT_ID = "port_id"
            PORT_TYPE = "port_type"

            TIMESTAMP = "ts"

            class ITEM:
                KEY = "key"
                VALUE = "value"
                FIELD = "field"
                TIMESTAMP = "ts"
                TAG = "tag"
                CHANNEL = "channel"
                MESSAGE = "message"

            class FIRMWARE:

                MCU_FAMILY = "fw_mcu_family"
                LIBRARY_VERSION = "fw_lib_ver"
                NAME = "fw_name"
                VERSION = "fw_ver"
                BUILD_TIME = "fw_build_time"
                CORE_VERSION = "fw_core_ver"
                CORTEX_VERSION = "fw_crtx_ver"
                USE_FREERTOS = "fw_freertos"

        class CONFIGURATIONS:
            SECURE_MODE = "scr_mod"
            SIGNER_CERTIFICATE = "crt_sig"
            DEVICE_CERTIFICATE = "dev_sig"

            SIGNATURE = "sgntr"

            PERSISTENT = "pers"
            ACKNOLEDGEMENT = "ack"
            PREFIX_ID = "prfx"

            TYPE = "type"

            class TYPES:

                APPLICATION = "appl"
                SETTING = "stng"
                RESERVED = "rsvd"

                TIMESERIES = "tse"
                TSTAGS = "tags"


    class RSP:

        RESPONSE_CODE = "rsp_code"

        class RSPS:
            _100: 100
            _101: 101
            _102: 102
            _200: 200
            _201: 201
            _202: 202
            _203: 203
            _204: 204
            _205: 205
            _206: 206
            _207: 207
            _208: 208
            _209: 209
            _210: 210

        class ARGUMENTS:

            DAEMON_VERSION = "dmn_ver"
            DAEMON_ENVIRONMENT = "dmn_env"

            ITEMS = "items"
            KEYS = "keys"

            CLIENTS = "clients"

        class CONFIGURATIONS:

            CHALLENGE = "chlng"

            TIMESTAMP = "ts"
            LOG_LEVEL = "log_lvl"


class PCK:
#    PACKET_110 = PACKET
    PACKET = {
        "1.1.0": PACKET_110,
        "1.0.0": PACKET_100
    }