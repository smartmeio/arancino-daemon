'''
SPDX-license-identifier: Apache-2.0

Copyright (C) 2019 SmartMe.IO

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
'''
from enum import Enum

#Definitions for Serial Protocol

#Special Chars
CHR_EOT = chr(4)            #End Of Transmission Char
CHR_SEP = chr(30)           #Separator Char

#Commands sent by the microcontroller running Arancino Library
CMD_SYS_START   = 'START' #Start Commmand

CMD_APP_GET     = 'GET'     #Get value at key
CMD_APP_SET     = 'SET'     #Set value at key
CMD_APP_SET_STD = 'SET'     #Set value at key (Standard as SET above)
CMD_APP_SET_PERS= 'SETPERS' #Set value at key (Persistent for User)
CMD_APP_DEL     = 'DEL'     #Delete one or multiple keys
CMD_APP_KEYS    = 'KEYS'    #Get keys by a pattern
CMD_APP_HGET    = 'HGET'    #
CMD_APP_HGETALL = 'HGETALL' #
CMD_APP_HKEYS   = 'HKEYS'   #
CMD_APP_HVALS   = 'HVALS'   #
CMD_APP_HDEL    = 'HDEL'    #
CMD_APP_HSET    = 'HSET'    #
CMD_APP_PUB     = 'PUB'     #
CMD_APP_FLUSH   = 'FLUSH'   #Flush the current Database, delete all the keys from the current Database

#Response codes to the microcontroller
RSP_OK          = '100'     #OK Response
RSP_HSET_NEW    = '101'     #Set value into a new field
RSP_HSET_UPD    = '102'     #Set value into an existing field

#Error codes
ERR             = '200'     #Generic Error
ERR_NULL        = '201'     #Null value
ERR_SET         = '202'     #Error during SET
ERR_CMD_NOT_FND = '203'     #Command Not Found
ERR_CMD_NOT_RCV = '204'     #Command Not Received
ERR_CMD_PRM_NUM = '205'     #Invalid parameter number
ERR_REDIS       = '206'     #Generic Redis Error
ERR_REDIS_KEY_EXISTS_IN_STD         = '207'     #Key exists in the Standard Data Store
ERR_REDIS_KEY_EXISTS_IN_PERS        = '208'     #Key exists in the Persistent Data Store
ERR_NON_COMPATIBILITY               = '209'     #Non compatibility between Arancino Module and Library

#Complete list of available commands
__COMMANDLIST = [ CMD_SYS_START,
                CMD_APP_GET,
                CMD_APP_SET,
                CMD_APP_SET_STD,
                CMD_APP_SET_PERS,
                CMD_APP_DEL,
                CMD_APP_KEYS,
                CMD_APP_HGET,
                CMD_APP_HGETALL,
                CMD_APP_HKEYS,
                CMD_APP_HVALS,
                CMD_APP_HDEL,
                CMD_APP_HSET,
                CMD_APP_PUB,
                CMD_APP_FLUSH]

#Characters for Reserverd keys def
RSVD_CHARS = "___"

#Reserved keys
RSVD_KEY_MONITOR    = RSVD_CHARS + "MONITOR" + RSVD_CHARS
RSVD_KEY_LIBVERSION = RSVD_CHARS + "LIBVERS" + RSVD_CHARS
RSVD_KEY_MODVERSION = RSVD_CHARS + "MODVERS" + RSVD_CHARS

#Reseverd keys list
__RESERVEDKEYSLIST  = [ RSVD_KEY_MONITOR,
                        RSVD_KEY_LIBVERSION,
                        RSVD_KEY_MODVERSION ]

def getCommandsList():
    return __COMMANDLIST

def getReservedKeysList():
    return __RESERVEDKEYSLIST

#Keys used in to store port information into devicestore

# additional metadata keys
M_ID              = "M_ID"              # String
M_ENABLED         = "M_ENABLED"         # Boolean
M_AUTO_CONNECT    = "M_AUTO_CONNECT"    # Boolean
M_CONNECTED       = "M_CONNECTED"       # Boolean
M_PLUGGED         = "M_PLUGGED"         # Boolean
M_ALIAS           = "M_ALIAS"           # Boolean
M_DATETIME        = "M_DATETIME"        # Datetime #TODO contestualizzare in maniera piu opportuna questo campo: (ultima modifica? ultima rilevazione ?)
M_HIDE_DEVICE     = "M_HIDE_DEVICE"     # Boolean
M_LIB_VER         = "M_LIB_VER"         # String (version number)

# ports info keys
P_DEVICE          = "P_DEVICE"          # String
P_NAME            = "P_NAME"            # String
P_DESCRIPTION     = "P_DESCRIPTION"     # String
P_HWID            = "P_HWID"            # String
P_VID             = "P_VID"             # Number in Hex format
P_PID             = "P_PID"             # Number in Hex
P_SERIALNUMBER    = "P_SERIALNUMBER"    # String (Hex)
P_LOCATION        = "P_LOCATION"        # Number-Number
P_MANUFACTURER    = "P_MANUFACTURER"    # String
P_PRODUCT         = "P_PRODUCT"         # String
P_INTERFACE       = "P_INTERFACE"       # String

# object keys
#O_PORT            = "O_PORT" #ListPortInfo
#O_SERIAL          = "O_SERIAL" #SerialConnector


# ports_plugged positionals
#IDX_SERIAL_CONNECTOR = 0
#IDX_SERIAL_TRANSPORT = 1


# compatibilty matrix of Aracnino Module and Arancino Library

COMPATIBILITY_MATRIX_MOD = {
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
    "1.0.4": [">=0.2.0", ">=1.0.0-rc,<=1.*.*"],
    "1.1.0": [">=0.2.0", ">=1.0.0-rc,<=1.*.*"],
    "1.1.1": [">=0.2.0", ">=1.0.0-rc,<=1.*.*"],
    "1.2.0": [">=0.2.0", ">=1.0.0-rc,<=1.*.*"]
}
'''
COMPATIBILITY_MATRIX_LIB = {
    #LIBRARY: #MODULE
    "0.0.1" : ["0.0.1","0.0.2"],
    "0.0.2" : ["0.0.2"],
    "0.1.0" : ["0.1.0","0.1.1","0.1.2","0.1.3","0.1.4","0.1.5"],
    "1.0.0" : ["1.0.0"],
}
'''

class RedisInstancesType(Enum):
    VOLATILE = 1
    PERSISTENT = 2
    VOLATILE_PERSISTENT = 3
    DEFAULT = 3

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class SerialBaudrates(Enum):
    _57600      = 57600
    _128000     = 128000
    _1151200    = 1151200
    _4000000    = 4000000
