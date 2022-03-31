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


class ArancinoPacket_(ABC):
    """
    Usato per Arancino Command e Arancino Response, perche hanno la stessa struttura di base,
        si differenziano solo per "cmd" (Arancino Command) e "rsp_code" (Arancino Response)
    """

    def __init__(self, rawPacket: dict):
        if rawPacket:
            self.args = rawPacket["args"]
            self.cfg = rawPacket["cfg"]
            #self.raw = rawPacket
        else:
            self.args = {}
            self.cfg = {}
            #self.raw = {}

    """
    @property
    def raw(self):
        return self.__raw

    @raw.setter
    def raw(self, rawPacket: dict):
        self.__raw = rawPacket
        #pass
    """
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
    def check_args(self):
        pass


class ArancinoCommand_(ArancinoPacket_):

    def __init__(self, rawCommand: dict):
        super().__init__(rawPacket=rawCommand)
        if rawCommand:
            self.id = rawCommand["cmd"]
            self.raw = rawCommand
        else:
            self.id = {}
            self.raw = {}

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id: str):
        self.__id = id

#    """
    @property
    def raw(self):
        if not self.__raw:
            self.raw = {
                "id": self.id,
                "cfg": self.cfg,
                "args": self.args
        }
        return self.__raw
#    """

    @raw.setter
    def raw(self, rawPacket: dict):
        self.__raw = rawPacket
        #pass

    def check_args(self):
        pass


class ArancinoResponse_(ArancinoPacket_):

    def __init__(self, rawResponse: dict):
        super().__init__(rawPacket=rawResponse)
        if rawResponse:
            self.raw = rawResponse
            self.code = rawResponse["code"]
        else:
            self.raw = {}
            self.code = {}

    @property
    def code(self):
        return self.__code

    @code.setter
    def code(self, code: str):
        self.__code = code

    @property
    def raw(self):
        if not self.__raw:
            self.raw = {
                "code": self.code,
                "cfg": self.cfg,
                "args": self.args
        }
        return self.__raw

    @raw.setter
    def raw(self, rawPacket: dict):
        self.__raw = rawPacket
        #pass

    def check_args(self):
        pass


class ArancinoPacket(ABC):
    """
    Usato per Arancino Command e Arancino Response, perche hanno la stessa struttura di base,
        si differenziano solo per "cmd" (Arancino Command) e "rsp_code" (Arancino Response)
    """

    def __init__(self, packet: dict):

        self._packed_packet = None
        self._unpacked_packet = None

        if packet:

            self.args = packet["args"]
            self.cfg = packet["cfg"]

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


class ArancinoCommand(ArancinoPacket):

    def __init__(self, packet):

        if packet:

            if isinstance(packet, dict):

                self.id = packet["cmd"]

            elif isinstance(packet, bytes):

                # trasformo packet in dict
                packet = msgpack.unpackb(packet, use_list=True, raw=False)
                self.id = packet["cmd"]

            else:

                # Tipo non riconosciuto/accettato
                raise InvalidCommandException("Invalid Command type/format - Skipped", ArancinoCommandErrorCodes.ERR_CMD_TYPE)


        else:

            self.id = None

        super().__init__(packet=packet)


    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id: str):
        self.__id = id


    def _create_packet(self):

        pck = {}
        pck.update({PACKET.CMD.COMMAND_ID: self.id})
        pck.update({PACKET.CMD.CONFIGURATION: self.cfg})
        pck.update({PACKET.CMD.ARGUMENT: self.args})

        return pck


class ArancinoResponse(ArancinoPacket):

    def __init__(self, packet):

        if packet:

            if isinstance(packet, dict):

                self.code = packet["code"]

            elif isinstance(packet, bytes):

                # trasformo packet in dict
                packet = msgpack.unpackb(packet, use_list=True, raw=False)
                self.code = packet["code"]

            else:

                # Tipo non riconosciuto/accettato
                raise InvalidCommandException("Invalid Command type/format - Skipped", ArancinoCommandErrorCodes.ERR_CMD_TYPE)


        else:

            self.code = None

        super().__init__(packet=packet)

    @property
    def code(self):
        return self.__code

    @code.setter
    def code(self, code: int):
        self.__code = code


    def _create_packet(self):

        pck = {}
        pck.update({PACKET.RSP.RESPONSE_CODE: self.code})
        pck.update({PACKET.RSP.CONFIGURATION: self.cfg})
        pck.update({PACKET.RSP.ARGUMENT: self.args})

        return pck


class PACKET:

    class CMD:

        COMMAND_ID = "cmd"
        CONFIGURATION = "cfg"
        ARGUMENT = " args"

        class ARGUMENTS:

            ITEMS = "items"
            KEYS = "keys"
            PORT_ID = "port_id"
            PORT_TYPE = "port_type"

            KEY = "key"
            TIMESTAMP = "ts"

            class FIRMWARE:

                MCU_FAMILY = "fw_mcu_family"
                LIBRARY_VERSION = "fw_lib_ver"
                NAME = "fw_name"
                VERSION = "fw_ver"
                BUILD_TIME = "fw_build_time"
                CORE_VERSION = "fw_core_ver"
                CORTEX_VERSION = "fw_crtx_ver"

        class CONFIGURATIONS:
            SECURE_MODE = "scr_mod"
            SIGNER_CERTIFICATE = "crt_sig"
            DEVICE_CERTIFICATE = "dev_sig"

            SIGNATURE = "sgntr"

            PERSISTENT = "pers"
            ACKNOLEDGEMENT = "ack"

            TYPE = "type"

            class TYPES:

                APPLICATION = "appl"
                SETTING = "stng"
                RESERVED = "rsvd"


    class RSP:

        RESPONSE_CODE = "code"
        CONFIGURATION = "cfg"
        ARGUMENT = " args"


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
