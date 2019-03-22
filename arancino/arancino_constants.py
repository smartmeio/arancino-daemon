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

#Definitions for Serial Protocol

#Special Chars
CHR_EOT = chr(4)            #End Of Transmission Char
CHR_SEP = chr(30)           #Separator Char

#Commands sent by the microcontroller running Arancino Library
CMD_SYS_START   = 'START' #Start Commmand

CMD_APP_GET     = 'GET'     #Get value at key
CMD_APP_SET     = 'SET'     #Set value at key
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

#Reserved keys
RSVD_KEY_MONITOR = "___MONITOR___"
RSVD_KEY_LIBVERSION = "___LIBVERS___"
RSVD_KEY_MODVERSION = "___MODVERS___"

#Complete list of available commands
__COMMANDLIST = [ CMD_SYS_START,
                CMD_APP_GET,
                CMD_APP_SET,
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

def getCommandsList():
    return __COMMANDLIST


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
IDX_SERIAL_CONNECTOR = 0
IDX_SERIAL_TRANSPORT = 1