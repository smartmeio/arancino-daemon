'''

Copyright ® SmartMe.IO  2018

LICENSE HERE

Filename = arancino_properties.py
Author: Sergio Tomasello - sergio@smartme.io
Date: 2019 01 14

'''

#Definitions for Serial Protocol
CHR_EOT = chr(4)            #End Of Transmission Char
CHR_SEP = chr(30)           #Separator Char


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

RSP_OK          = '100'     #OK Response
RSP_HSET_NEW    = '101'     #Set value into a new field
RSP_HSET_UPD    = '102'     #Set value into an existing field

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