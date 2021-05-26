# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2019 smartme.IO

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

from enum import Enum


class RedisInstancesType(Enum):
    VOLATILE = 1
    PERSISTENT = 2
    VOLATILE_PERSISTENT = 3
    DEFAULT = 3

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class SerialBaudrates(Enum):
    _57600 = 57600
    _128000 = 128000
    _1151200 = 1151200
    _4000000 = 4000000


class ArancinoSpecialChars:
    # Special Chars
    CHR_EOT = chr(4)
    "End Of Transmission Char: identifies the end of the command"

    CHR_SEP = chr(30)
    "Separator Char: separates the commands id from arguments, and arguments themeself"

    CHR_ARR_SEP = chr(16)
    "Array Char: separates arguments data in case of array"

    CHR_NULL_VALUE = chr(25)
    "Representation of Null/None value"


class ArancinoReservedChars:
    #Characters for Reserverd keys def
    RSVD_CHARS = "___"

    # Reserved keys
    RSVD_KEY_MONITOR    = RSVD_CHARS + "MONITOR" + RSVD_CHARS
    RSVD_KEY_LIBVERSION = RSVD_CHARS + "LIBVERS" + RSVD_CHARS
    RSVD_KEY_MODVERSION = RSVD_CHARS + "MODVERS" + RSVD_CHARS
    RSVD_KEY_MODENVIRONMENT = RSVD_CHARS + "MODENV" + RSVD_CHARS
    RSVD_KEY_MODLOGLEVEL = RSVD_CHARS + "MODLOGLVL" + RSVD_CHARS
    RSVD_KEY_BLINK_ID = RSVD_CHARS + "BLNK_ID" + RSVD_CHARS

    # Reseverd keys list
    RESERVEDKEYSLIST = [RSVD_KEY_MONITOR,
                        RSVD_KEY_LIBVERSION,
                        RSVD_KEY_MODVERSION,
                        RSVD_KEY_MODENVIRONMENT,
                        RSVD_KEY_MODLOGLEVEL,
                        RSVD_KEY_BLINK_ID
                        ]


class ArancinoCommandErrorCodes:
    # Error codes
    ERR = '200'
    "Generic Error"

    ERR_NULL = '201'
    "Null value"

    ERR_SET = '202'
    "Error during SET"

    ERR_CMD_NOT_FND = '203'
    "Command Not Found"

    ERR_CMD_NOT_RCV = '204'
    "Command Not Received"

    ERR_CMD_PRM_NUM = '205'
    "Invalid parameter number"

    ERR_REDIS = '206'
    "Generic Redis Error"

    ERR_REDIS_KEY_EXISTS_IN_STD = '207'
    "Key exists in the Standard Data Store"

    ERR_REDIS_KEY_EXISTS_IN_PERS = '208'
    "Key exists in the Persistent Data Store"

    ERR_NON_COMPATIBILITY = '209'
    "Non compatibility between Arancino Daemon and Library"

    ERR_INVALID_ARGUMENTS = '210'
    "Generic Invalid Arguments"

    ERR_VALUE = '211'
    "Invalid Value"

    ERRORS_CODE_LIST = [
                            ERR,
                            ERR_NULL,
                            ERR_SET,
                            ERR_CMD_NOT_FND,
                            ERR_CMD_NOT_RCV,
                            ERR_CMD_PRM_NUM,
                            ERR_REDIS,
                            ERR_REDIS_KEY_EXISTS_IN_STD,
                            ERR_REDIS_KEY_EXISTS_IN_PERS,
                            ERR_NON_COMPATIBILITY,
                            ERR_INVALID_ARGUMENTS,
                            ERR_VALUE,
                        ]


class ArancinoCommandResponseCodes:
    RSP_OK = '100'
    "OK Response"

    RSP_HSET_NEW = '101'
    "Set value into a new field"

    RSP_HSET_UPD = '102'
    "Set value into an existing field"

    RESPONSES_CODE_LIST = [RSP_OK,
                           RSP_HSET_NEW,
                           RSP_HSET_UPD]


class ArancinoOperators:

    EQUAL = "EQ"
    LESS_THAN = "LT"
    LESS_THAN_OR_EQUAL = "LTE"
    GREATER_THAN = "GT"
    GREATER_THAN_OR_EQUAL = "GTE"
    NOT_EQUAL = "NEQ"
    BETWEEN = "BET"


class ArancinoCommandIdentifiers:
    # Commands sent by the Port w/ Cortex Protocol

    # Init commands
    __CMD_SYS_START = 'START'
    CMD_SYS_START = {"id": __CMD_SYS_START, "args": 2, "op": ArancinoOperators.EQUAL}
    "Start Commmand"

    # Simple Operation Commands
    __CMD_APP_GET = 'GET'
    CMD_APP_GET = {"id": __CMD_APP_GET, "args": 1, "op": ArancinoOperators.EQUAL}
    "Get value at key"

    __CMD_APP_GET_RSVD = 'GETRSVD'
    CMD_APP_GET_RSVD = {"id": __CMD_APP_GET_RSVD, "args": 1, "op": ArancinoOperators.EQUAL}
    "Get value at reserverd key"

    __CMD_APP_SET = 'SET'
    CMD_APP_SET = {"id": __CMD_APP_SET, "args": 2, "op": ArancinoOperators.EQUAL}
    "Set value at key"

    __CMD_APP_SET_STD = 'SET'
    CMD_APP_SET_STD = {"id": __CMD_APP_SET_STD, "args": 2, "op": ArancinoOperators.EQUAL}
    "Set value at key (Standard as SET above)"

    __CMD_APP_SET_PERS = 'SETPERS'
    CMD_APP_SET_PERS = {"id": __CMD_APP_SET_PERS, "args": 2, "op": ArancinoOperators.EQUAL}
    "Set value at key (Persistent for User)"

    __CMD_APP_SET_RSVD = 'SETRSVD'
    CMD_APP_SET_RSVD = {"id": __CMD_APP_SET_RSVD, "args": 2, "op": ArancinoOperators.EQUAL}
    "Set value at key (Reserved keys)"

    __CMD_APP_DEL = 'DEL'
    CMD_APP_DEL = {"id": __CMD_APP_DEL, "args": 1, "op": ArancinoOperators.EQUAL}
    "Delete one or multiple keys"

    __CMD_APP_KEYS = 'KEYS'
    CMD_APP_KEYS = {"id": __CMD_APP_KEYS, "args": 1, "op": ArancinoOperators.EQUAL}
    "Get keys by a pattern"

    # Hashtable Commands
    __CMD_APP_HGET = 'HGET'  #
    CMD_APP_HGET = {"id": __CMD_APP_HGET, "args": 2, "op": ArancinoOperators.EQUAL}

    __CMD_APP_HGETALL = 'HGETALL'  #
    CMD_APP_HGETALL = {"id": __CMD_APP_HGETALL, "args": 1, "op": ArancinoOperators.EQUAL}

    __CMD_APP_HKEYS = 'HKEYS'  #
    CMD_APP_HKEYS = {"id": __CMD_APP_HKEYS, "args": 1, "op": ArancinoOperators.EQUAL}

    __CMD_APP_HVALS = 'HVALS'  #
    CMD_APP_HVALS = {"id": __CMD_APP_HVALS, "args": 1, "op": ArancinoOperators.EQUAL}

    __CMD_APP_HDEL = 'HDEL'  #
    CMD_APP_HDEL = {"id": __CMD_APP_HDEL, "args": 2, "op": ArancinoOperators.EQUAL}

    __CMD_APP_HSET = 'HSET'  #
    CMD_APP_HSET = {"id": __CMD_APP_HSET, "args": 3, "op": ArancinoOperators.EQUAL}

    __CMD_APP_HSET_STD = 'HSET'  #
    CMD_APP_HSET_STD = {"id": __CMD_APP_HSET_STD, "args": 3, "op": ArancinoOperators.EQUAL}

    __CMD_APP_HSET_PERS = 'HSETPERS'  #
    CMD_APP_HSET_PERS = {"id": __CMD_APP_HSET_PERS, "args": 3, "op": ArancinoOperators.EQUAL}

    # Other Commands
    __CMD_APP_PUB = 'PUB'
    CMD_APP_PUB = {"id": __CMD_APP_PUB, "args": 2, "op": ArancinoOperators.EQUAL}
    "Publish a message to a channel"

    __CMD_APP_FLUSH = 'FLUSH'
    CMD_APP_FLUSH = {"id": __CMD_APP_FLUSH, "args": 0, "op": ArancinoOperators.EQUAL}
    "Flush the current Database, delete all the keys from the current Database"

    __CMD_APP_MSET = 'MSET'
    CMD_APP_MSET = {"id": __CMD_APP_MSET, "args": 2, "op": ArancinoOperators.EQUAL}
    "Sets more than one value at the specified keys, at the same time"

    __CMD_APP_MSET_STD = 'MSET'
    CMD_APP_MSET_STD = {"id": __CMD_APP_MSET_STD, "args": 2, "op": ArancinoOperators.EQUAL}
    "Sets more than one value at the specified keys, at the same time (Standard as SET above)"

    __CMD_APP_MSET_PERS = 'MSETPERS'
    CMD_APP_MSET_PERS = {"id": __CMD_APP_MSET_PERS, "args": 2, "op": ArancinoOperators.EQUAL}
    "Sets more than one value at the specified keys, at the same time (Persistent for User)"

    __CMD_APP_MGET = 'MGET'
    CMD_APP_MGET = {"id": __CMD_APP_MGET, "args": 1, "op": ArancinoOperators.EQUAL}
    "Sets more than one key value at the same time"

    __CMD_APP_STORETAGS = 'STORETAGS'
    CMD_APP_STORETAGS = {"id": __CMD_APP_STORETAGS, "args": 3, "args2": 4, "op": ArancinoOperators.BETWEEN}
    "Store tags for a Time Series at key"

    __CMD_APP_STORE = 'STORE'
    CMD_APP_STORE = {"id": __CMD_APP_STORE, "args": 2, "args2": 3, "op": ArancinoOperators.BETWEEN}
    "Store the current value in TimeSeries data structure at the key"

    __CMD_APP_MSTORE = 'MSTORE'
    CMD_APP_MSTORE = {"id": __CMD_APP_MSTORE, "args": 2, "args2": 3, "op": ArancinoOperators.BETWEEN}
    "Store more than one value in TimeSeries data structure at the key"

    COMMANDS_DICT = {
        __CMD_SYS_START: CMD_SYS_START,
        __CMD_APP_GET: CMD_APP_GET,
        __CMD_APP_GET_RSVD: CMD_APP_GET_RSVD,
        __CMD_APP_SET: CMD_APP_SET,
        __CMD_APP_SET_STD: CMD_APP_SET_STD,
        __CMD_APP_SET_PERS: CMD_APP_SET_PERS,
        __CMD_APP_SET_RSVD: CMD_APP_SET_RSVD,
        __CMD_APP_DEL: CMD_APP_DEL,
        __CMD_APP_KEYS: CMD_APP_KEYS,
        __CMD_APP_HGET: CMD_APP_HGET,
        __CMD_APP_HGETALL: CMD_APP_HGETALL,
        __CMD_APP_HKEYS: CMD_APP_HKEYS,
        __CMD_APP_HVALS: CMD_APP_HVALS,
        __CMD_APP_HDEL: CMD_APP_HDEL,
        __CMD_APP_HSET: CMD_APP_HSET,
        __CMD_APP_HSET_STD: CMD_APP_HSET_STD,
        __CMD_APP_HSET_PERS: CMD_APP_HSET_PERS,
        __CMD_APP_PUB: CMD_APP_PUB,
        __CMD_APP_FLUSH: CMD_APP_FLUSH,
        __CMD_APP_MSET: CMD_APP_MSET,
        __CMD_APP_MSET_STD: CMD_APP_MSET_STD,
        __CMD_APP_MSET_PERS: CMD_APP_MSET_PERS,
        __CMD_APP_MGET: CMD_APP_MGET,
        __CMD_APP_STORE: CMD_APP_STORE,
        __CMD_APP_STORETAGS: CMD_APP_STORETAGS,
        __CMD_APP_MSTORE: CMD_APP_MSTORE,
    }
    "Complete dictionary of all available commands: " \
    "{ 'SET': {'id': 'SET', 'args': 2} , ... }"

    COMMANDS_LIST = [__CMD_SYS_START,
                     __CMD_APP_GET,
                     __CMD_APP_GET_RSVD,
                     __CMD_APP_SET,
                     __CMD_APP_SET_STD,
                     __CMD_APP_SET_PERS,
                     __CMD_APP_SET_RSVD,
                     __CMD_APP_DEL,
                     __CMD_APP_KEYS,
                     __CMD_APP_HGET,
                     __CMD_APP_HGETALL,
                     __CMD_APP_HKEYS,
                     __CMD_APP_HVALS,
                     __CMD_APP_HDEL,
                     __CMD_APP_HSET,
                     __CMD_APP_HSET_STD,
                     __CMD_APP_HSET_PERS,
                     __CMD_APP_PUB,
                     __CMD_APP_FLUSH,
                     __CMD_APP_MSET,
                     __CMD_APP_MSET_STD,
                     __CMD_APP_MSET_PERS,
                     __CMD_APP_MGET,
                     __CMD_APP_STORE,
                     __CMD_APP_STORETAGS,
                     __CMD_APP_MSTORE,
                     ]
    "Complete list of all available commands:" \
    "[ 'SET', 'GET', ... ]"


class ArancinoDBKeys:
    # Keys used in to store port information into devicestore

    # BASE ARANCINO METADATA (B)ase
    B_ID = "B_ID"                           # String
    B_PORT_TYPE = "B_PORT_TYPE"             # Num
    B_CREATION_DATE = "S_CREATION_DATE"     # Datetime
    B_LIB_VER = "B_LIB_VER"                 # String
    B_FW_VER = "B_FW_VER"                   # String
    B_FW_NAME = "B_FW_NAME"                 # String
    B_FW_COMPILE_DATE = "B_FW_COMPILE_DATE" # Datetime
    B_FW_CORE_VER = "B_FW_CORE_VER"         # String
    B_MCU_FAMILY = "B_MCU_FAMILY"           # String
    B_ATTRIBUTES = "B_ATTRIBUTES"           # Dict
    
    # LINK ARANCINO METADATA (L)ink
    L_DEVICE = "L_DEVICE"                   # String

    # BASE ARANCINO STATUS METADATA (S)tatus
    S_CONNECTED = "S_CONNECTED"             # Boolean
    S_PLUGGED = "S_PLUGGED"                 # Boolean
    S_LAST_USAGE_DATE = "S_LAST_USAGE_DATE" # Datetime
    S_UPTIME = "S_UPTIME"                   # Datetime
    S_COMPATIBILITY = "S_COMPATIBILITY"     # Boolean
    S_STARTED = "S_STARTED"                 # Boolean

    # BASE ARANCINO CONFIGURATION METADATA (C)Configuration
    C_ENABLED = "C_ENABLED"                 # Boolean
    C_ALIAS = "C_ALIAS"                     # Boolean
    C_HIDE_DEVICE = "C_HIDE_DEVICE"         # Boolean

    # SERIAL ARANCINO PORT METADATA (P)Port
    P_NAME = "P_NAME"                       # String
    P_DESCRIPTION = "P_DESCRIPTION"         # String
    P_HWID = "P_HWID"                       # String
    P_VID = "P_VID"                         # Number in Hex format
    P_PID = "P_PID"                         # Number in Hex
    P_SERIALNUMBER = "P_SERIALNUMBER"       # String (Hex)
    P_LOCATION = "P_LOCATION"               # Number-Number
    P_MANUFACTURER = "P_MANUFACTURER"       # String
    P_PRODUCT = "P_PRODUCT"                 # String
    P_INTERFACE = "P_INTERFACE"             # String
    P_DEVICE = "P_DEVICE"                   # String


    __DB_KEY_NAMES = {
        # BASE ARANCINO METADATA (B)ase
        B_ID: "B_ID",                           # String
        B_PORT_TYPE: "B_PORT_TYPE",             # Num
        B_CREATION_DATE: "S_CREATION_DATE",     # Datetime
        B_LIB_VER: "B_LIB_VER",                 # String
        B_FW_VER: "B_FW_VER",                   # String
        B_FW_NAME: "B_FW_NAME",                 # String
        B_FW_COMPILE_DATE: "B_FW_COMPILE_DATE", # Datetime
        B_FW_CORE_VER: "B_FW_CORE_VER",         # String
        B_MCU_FAMILY: "B_MCU_FAMILY",           # String
        B_ATTRIBUTES: "B_ATTRIBUTES",           # Dict
        
        # LINK ARANCINO METADATA (L)ink
        L_DEVICE: "L_DEVICE",                   # String

        # BASE ARANCINO STATUS METADATA (S)tatus
        S_CONNECTED: "S_CONNECTED",             # Boolean
        S_PLUGGED: "S_PLUGGED",                 # Boolean
        S_LAST_USAGE_DATE: "S_LAST_USAGE_DATE", # Datetime
        S_UPTIME: "S_UPTIME",                   # Datetime
        S_COMPATIBILITY: "S_COMPATIBILITY",     # Boolean
        S_STARTED: "S_STARTED",                 # Boolean

        # BASE ARANCINO CONFIGURATION METADATA (C)Configuration
        C_ENABLED: "C_ENABLED",                 # Boolean
        C_ALIAS: "C_ALIAS",                     # Boolean
        C_HIDE_DEVICE: "C_HIDE_DEVICE",         # Boolean

        # SERIAL ARANCINO PORT METADATA (P)Port
        P_NAME: "P_NAME",                       # String
        P_DESCRIPTION: "P_DESCRIPTION",         # String
        P_HWID: "P_HWID" ,                      # String
        P_VID: "P_VID",                         # Number in Hex format
        P_PID: "P_PID",                         # Number in Hex
        P_SERIALNUMBER: "P_SERIALNUMBER",       # String (Hex)
        P_LOCATION: "P_LOCATION",               # Number-Number
        P_MANUFACTURER: "P_MANUFACTURER",       # String
        P_PRODUCT: "P_PRODUCT",                 # String
        P_INTERFACE: "P_INTERFACE",             # String
        P_DEVICE: "P_DEVICE",                   # String
    }

    __DB_KEY_DESC = {
        # BASE ARANCINO METADATA (B)ase
        B_ID: "Id",                                 # String
        B_PORT_TYPE: "Type",                        # Num
        B_CREATION_DATE: "Creation Date",           # Datetime
        B_LIB_VER: "Library Version",               # String
        B_FW_VER: "Fimrware Version",               # String
        B_FW_NAME: "Firmware Name",                 # String
        B_FW_COMPILE_DATE: "Firmware Compile Date", # Datetime
        B_FW_CORE_VER: "Firmware Core Version",     # String
        B_MCU_FAMILY: "Microcontroller Family",     # String
        B_ATTRIBUTES: "Generic Port Attributes",    # Dict

        # LINK ARANCINO METADATA (L)ink
        L_DEVICE: "Connection Id",                  # String

        # BASE ARANCINO STATUS METADATA (S)tatus
        S_CONNECTED: "Connected",                   # Boolean
        S_PLUGGED: "Plugged",                       # Boolean
        S_LAST_USAGE_DATE: "Last Usage Date",       # Datetime
        S_UPTIME: "Uptime",                         # Datetime
        S_COMPATIBILITY: "Compatibility",           # Boolean
        S_STARTED: "Started",                       # Boolean

        # BASE ARANCINO CONFIGURATION METADATA (C)Configuration
        C_ENABLED: "Enabled",                       # Boolean
        C_ALIAS: "Alias",                           # Boolean
        C_HIDE_DEVICE: "Hidden",                    # Boolean

        # SERIAL ARANCINO PORT METADATA (P)Port
        P_NAME: "Serial Name",                      # String
        P_DESCRIPTION: "Serial Port Description",   # String
        P_HWID: "Serial Port Hardware Id",          # String
        P_VID: "Serial Port Vendor Id",             # Number in Hex format
        P_PID: "Serial Port Product Id",            # Number in Hex
        P_SERIALNUMBER: "Serial Port Serial Number",# String (Hex)
        P_LOCATION: "Serial Port Location",         # Number-Number
        P_MANUFACTURER: "Serial Port Manufcaturer", # String
        P_PRODUCT: "Serial Port Product Name",      # String
        P_INTERFACE: "Serial Port Interface",       # String
        P_DEVICE: "Serial Port Device Name",        # String
    }


class ArancinoApiResponseCode:

    def __init__(self):
        pass

    OK_ALREADY_ENABLED = 1
    OK_ENABLED = 2

    OK_ALREADY_DISABLED = 3
    OK_DISABLED = 4

    OK_ALREADY_CONNECTED = 5
    OK_CONNECTED = 6

    OK_ALREADY_DISCONNECTED = 7
    OK_DISCONNECTED = 8

    OK_RESET = 9
    OK_RESET_NOT_PROVIDED = 10

    OK_UPLOAD = 11
    OK_UPLOAD_NOT_PROVIDED = 12

    OK_ALREADY_HIDDEN = 13
    OK_HIDDEN = 14

    OK_ALREADY_SHOWN = 15
    OK_SHOWN = 16

    OK_CONFIGURATED = 17

    OK_ARANCINO_CONFIGURATED = 18

    OK_ARANCINO_PORT_IDENTIFYING = 19

    ERR_PORT_NOT_FOUND = 20
    ERR_CAN_NOT_CONNECT_PORT_DISABLED = 21
    ERR_GENERIC = 22
    ERR_RESET = 23
    ERR_UPLOAD = 24
    ERR_NO_CONFIG_PROVIDED = 25
    ERR_NO_ARANCINO_CONFIG_SECTION_PROVIDED = 26
    ERR_NO_ARANCINO_CONFIG_OPTION_PROVIDED = 27
    ERR_NO_ARANCINO_CONFIG_VALUE_PROVIDED = 28

    __USER_MESSAGES = {
        OK_ALREADY_ENABLED: "Selected port is already enabled.",
        OK_ENABLED: "Port enabled successfully.",

        OK_ALREADY_DISABLED: "Selected port is already disabled.",
        OK_DISABLED: "Port disabled successfully.",

        OK_ALREADY_CONNECTED: "Selected port is already connected.",
        OK_CONNECTED: "Port connected successfully.",

        OK_ALREADY_DISCONNECTED: "Selected port is already disconnected.",
        OK_DISCONNECTED: "Port disconnected successfully.",

        OK_RESET: "Port reset successfully.",
        OK_RESET_NOT_PROVIDED: "This port does not provide reset operation",

        OK_UPLOAD: "Firmware uploaded successfully.",
        OK_UPLOAD_NOT_PROVIDED: "This port does not provide upload operation",

        ERR_PORT_NOT_FOUND: "Sorry, can not find specified port. Probably port was disconnected or unplugged during this operation.",
        ERR_CAN_NOT_CONNECT_PORT_DISABLED: "Sorry, can not connect a disabled port, first enable it.",
        ERR_GENERIC: "Sorry, an error was occurred during this operation.",
        ERR_RESET: "Sorry, an error was occurred during this operation.",
        ERR_UPLOAD: "Sorry, an error was occurred during this operation.",
        ERR_NO_CONFIG_PROVIDED: "Sorry, no configuration params found during this operation",

        ERR_NO_ARANCINO_CONFIG_SECTION_PROVIDED: "Sorry, no section configuration found during this operation",
        ERR_NO_ARANCINO_CONFIG_OPTION_PROVIDED: "Sorry, no option configuration found during this operation",
        ERR_NO_ARANCINO_CONFIG_VALUE_PROVIDED: "Sorry, no value configuration found during this operation",


        OK_ALREADY_HIDDEN: "Selected port is already hidden",
        OK_HIDDEN: "Port hidden successfully",

        OK_ALREADY_SHOWN: "Selected port is already shown",
        OK_SHOWN: "Port shown successfully",

        OK_CONFIGURATED: "Port configured successfully",

        OK_ARANCINO_CONFIGURATED: "Arancino configured successfully",

        OK_ARANCINO_PORT_IDENTIFYING: "Start Port Identifying"

    }

    __INTERNAL_MESSAGES = {
        OK_ALREADY_ENABLED: "Selected port is already enabled.",
        OK_ENABLED: "Port enabled successfully.",

        OK_ALREADY_DISABLED: "Selected port is already disabled.",
        OK_DISABLED: "Port disabled successfully.",

        OK_ALREADY_CONNECTED: "Selected port is already connected.",
        OK_CONNECTED: "Port connected successfully.",

        OK_ALREADY_DISCONNECTED: "Selected port is already disconnected.",
        OK_DISCONNECTED: "Port disconnected successfully.",

        OK_RESET: "Port reset successfully ",
        OK_RESET_NOT_PROVIDED: "This port does not provide reset operation",

        OK_UPLOAD: "Firmware uploaded successfully.",
        OK_UPLOAD_NOT_PROVIDED: "This port does not provide upload operation",

        ERR_PORT_NOT_FOUND: "Sorry, can not find specified port. Probably port was disconnected or unplugged during this operation.",
        ERR_CAN_NOT_CONNECT_PORT_DISABLED: "Sorry, can not connect a disabled port, first enable it.",
        ERR_GENERIC: None,
        ERR_RESET: None,
        ERR_UPLOAD: None,
        ERR_NO_CONFIG_PROVIDED: "Sorry, no configuration params found during this operation",

        ERR_NO_ARANCINO_CONFIG_SECTION_PROVIDED: "Sorry, no section configuration found during this operation",
        ERR_NO_ARANCINO_CONFIG_OPTION_PROVIDED: "Sorry, no option configuration found during this operation",
        ERR_NO_ARANCINO_CONFIG_VALUE_PROVIDED: "Sorry, no value configuration found during this operation",

        OK_ALREADY_HIDDEN: "Selected port is already hidden",
        OK_HIDDEN: "Port hidden successfully",

        OK_ALREADY_SHOWN: "Selected port is already shown",
        OK_SHOWN: "Port shown successfully",

        OK_CONFIGURATED: "Port configured successfully",

        OK_ARANCINO_CONFIGURATED: "Arancino configured successfully",

        OK_ARANCINO_PORT_IDENTIFYING: "Start Port Identifying"

    }

    def USER_MESSAGE(self, response_code):
        return self.__USER_MESSAGES[response_code]

    def INTERNAL_MESSAGE(self, response_code):
        return self.__INTERNAL_MESSAGES[response_code]


class ArancinoPortAttributes:

    LibraryVersion = "LIB_VER"
    MicrocontrollerFamily = "MCU_FAMILY"
    FirmwareName = "FW_NAME"
    FirmwareVersion = "FW_VER"
    FirmwareBuildTime = "FW_BUILD_TIME"
    FirmwareCoreVersion = "FW_CORE_VER"

    AttributesKeysList = [LibraryVersion,
                            MicrocontrollerFamily,
                            FirmwareName,
                            FirmwareVersion,
                            FirmwareBuildTime,
                            FirmwareCoreVersion]


COMPATIBILITY_MATRIX_MOD_SERIAL = {
    #MODULE : #LIBRARY
#    "0.0.1" : ["0.0.1"],
#    "0.0.2" : ["0.0.1","0.0.2"],
#    "0.1.0" : ["0.1.0"],
#    "0.1.1" : ["0.1.0"],
#    "0.1.2" : ["0.1.0"],
#    "0.1.3" : ["0.1.0"],
#    "0.1.4" : ["0.1.0"],
#    "0.1.5" : ["0.1.0"],
    "1.0.0": ["1.0.0.RC1", "1.0.0"],    # 1.0.0.RC1 non-standard sem ver 2.0.0
    "1.0.1": [">=1.0.0-rc,<=1.*.*"],
    "1.0.2": [">=1.0.0-rc,<=1.*.*"],
    "1.0.3": [">=1.0.0-rc,<=1.*.*"],
    "1.0.4": ["=0.2.0"],
    "1.1.0": ["=0.2.0"],
    "1.1.1": ["=0.2.0"],
    "1.2.0": ["=0.2.0"],
    "1.2.1": ["=0.2.0"],
    "2.0.0": [">=0.3.0,<1.0.0", ">=1.2.0,<2.0.0"],
    "2.1.0": [">=0.4.0,<1.0.0", ">=1.3.0,<2.0.0"],
    "2.1.1": [">=0.4.0,<1.0.0", ">=1.3.0,<2.0.0"],
    "2.1.2": [">=0.4.0,<1.0.0", ">=1.3.0,<2.0.0"],
    "2.1.3": [">=0.4.0,<1.0.0", ">=1.3.0,<2.0.0"],
    "2.1.4": [">=0.4.0,<1.0.0", ">=1.3.0,<2.0.0"],
    "2.2.0": [">=0.4.0,<1.0.0", ">=1.3.0"],
    "2.3.0": [">=1.3.0", ">=1.3.0"],
    "2.4.0": [">=2.0.0"],
    #"2.0.0": ["<0.3.0", ">=1.2.0"], # for tests
}


COMPATIBILITY_MATRIX_MOD_TEST = {
    #MODULE : #LIBRARY
    "2.0.0": [">=1.0.0"],
    "2.1.0": [">=1.0.0"],
    "2.1.1": [">=1.0.0"],
    "2.1.2": [">=1.0.0"],
    "2.1.3": [">=1.0.0"],
    "2.1.4": [">=1.0.0"],
    "2.2.0": [">=1.0.0"],
    "2.3.0": [">=1.0.0"],
    "2.4.0": [">=1.0.0"],
}


SUFFIX_TMSTP = "TSTMP"
SUFFIX_TAG = "TSTAG"
SUFFIX_LBL = "TSLBL"