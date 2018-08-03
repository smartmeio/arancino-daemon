

#Definitions for Serial Protocol
CHR_EOT = chr(4)        #End Of Transmission Char
CHR_SEP = chr(30)       #Separator Char

CMD_SYS_START = 'START' #Start Commmand

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

RSP_OK          = '100'     #OK Response
RSP_HSET_NEW    = '101'     #Set value into a new field
RSP_HSET_UPD    = '102'     #Set value into an existing field

RSP_KO = 'KO'   #KO Response

ERR             = '200'     #Generic Error
ERR_NULL        = '201'     #Null value
ERR_SET         = '202'     #Error during SET
ERR_CMD_FOUND   = '203'     #Command Not Found

import redis

class SerialManagerUnitTest():

    def __init__(self):
        self.datastore = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    def _parseCommands(self, command):
        # decode the received commands
        cmd = command.strip()#command.decode().strip()

        # splits command by separator char
        cmd = cmd.split(CHR_SEP)

        # and then execute the command
        return self._execCommand(cmd)


    def _execCommand(self, cmd):
        idx = len(cmd)
        parameters = cmd[1:idx]

        # SET
        if cmd[0] == CMD_APP_SET:
            return self._OPTS_SET(parameters)
        # GET
        elif cmd[0] == CMD_APP_GET:
            return self._OPTS_GET(parameters)
        # DEL
        elif cmd[0] == CMD_APP_DEL:
            return self._OPTS_DEL(parameters)
        # KEYS
        elif cmd[0] == CMD_APP_KEYS:
            return self._OPTS_KEYS(parameters)
        # HSET
        elif cmd[0] == CMD_APP_HSET:
            return self._OPTS_HSET(parameters)
        # HGET
        elif cmd[0] == CMD_APP_HGET:
            return self._OPTS_HGET(parameters)
        # HGETALL
        elif cmd[0] == CMD_APP_HGETALL:
            return self._OPTS_HGETALL(parameters)
        # HVALS
        elif cmd[0] == CMD_APP_HVALS:
            return self._OPTS_HVALS(parameters)
        # HDEL
        elif cmd[0] == CMD_APP_HDEL:
            return self._OPTS_HDEL(parameters)

        # Default
        else:
            return ERR_CMD_FOUND + CHR_SEP
    # SET
    def _OPTS_SET(self, params):
        '''
        Set key to hold the string value. If key already holds a value,
        it is overwritten, regardless of its type. Any previous time to live
        associated with the key is discarded on successful SET operation.
            https://redis.io/commands/set

        MCU → SET#<key>#<value>

        MCU ← 100@ (OK)
        MCU ← 202@ (KO)
        '''

        key = params[0]
        value = params[1]

        rsp = self.datastore.set(key, value)
        if rsp:
            # return ok response
            return RSP_OK + CHR_EOT
        else:
            # return the error code
            return ERR_SET + CHR_EOT


    # GET
    def _OPTS_GET(self, args):
        '''
        Get the value of key. If the key does not exist the special value nil is returned.
        An error is returned if the value stored at key is not a string,
        because GET only handles string values.
            https://redis.io/commands/get

        MCU → GET#<key>

        MCU ← 100#<value>@ (OK)
        MCU ← 201@  (KO)
        '''

        key = args[0]

        rsp = self.datastore.get(key)

        if rsp is not None:
            # return the value
            return RSP_OK + CHR_SEP + str(rsp) + CHR_EOT
        else:
            # return the error code
            return ERR_NULL + CHR_EOT


    # DEL
    def _OPTS_DEL(self, args):
        '''
        Removes the specified keys. A key is ignored if it does not exist.
            https://redis.io/commands/del

        MCU → DEL#<key-1>[#<key-2>#<key-n>]

        MCU ← 100#<num-of-deleted-keys>@
        '''

        num = self.datastore.delete(*args)
        return RSP_OK + CHR_SEP + str(num) + CHR_EOT


    # KEYS
    def _OPTS_KEYS(self, args):
        '''
        Returns all keys matching pattern.
            https://redis.io/commands/keys

        MCU → KEYS[#<pattern>]

        MCU ← 100[#<key-1>#<key-2>#<key-n>]@
        '''

        if len(args) == 0:
            pattern = '*'  # w/o pattern
        else:
            pattern = args[0]  # w/ pattern

        keys = self.datastore.keys(pattern)

        if len(keys) > 0:
            return RSP_OK + CHR_SEP + CHR_SEP.join(keys) + CHR_EOT
        else:
            return RSP_OK + CHR_EOT


    # HSET
    def _OPTS_HSET(self, args):
        '''
        Sets field in the hash stored at key to value.
        If key does not exist, a new key holding a hash is created.
        If field already exists in the hash, it is overwritten.
            https://redis.io/commands/hset

        MCU → HSET#<key>#<field>#<value>

        MCU ← 101@
        MCU ← 102@
        '''

        key = args[0]
        field = args[1]
        value = args[2]

        rsp = self.datastore.hset(key, field, value)

        if rsp == 1:
            return RSP_HSET_NEW + CHR_EOT
        else:  # 0
            return RSP_HSET_UPD + CHR_EOT


    # HGET
    def _OPTS_HGET(self, args):
        # TODO gestire eccezzione
        # redis.exceptions.ResponseError: WRONGTYPE Operation against a key holding the wrong kind of value
        # scatta quando faccio la get (semplice) di una chiave che non contiene un valore semplice ma una hashtable
        '''
        Returns the value associated with field in the hash stored at key.
            https://redis.io/commands/hget

        MCU → HGET#<key>#<field>

        MCU ← 100#<value>@
        MCU ← 201@

        '''

        key = args[0]
        field = args[1]

        value = self.datastore.hget(key, field)

        if value is not None:
            # return the value
            return RSP_OK + CHR_SEP + str(value) + CHR_EOT
        else:
            # return the error code
            return ERR_NULL + CHR_EOT

    # HGETALL
    def _OPTS_HGETALL(self, args):
        '''
        Returns all fields and values of the hash stored at key.
        In the returned value, every field name is followed by its value,
        so the length of the reply is twice the size of the hash.
            https://redis.io/commands/hgetall

        MCU → HGETALL#<key>

        MCU ← 100[#<field-1>#<value-1>#<field-2>#<value-2>]@
        '''

        key = args[0]

        rsp_str = ""

        data = self.datastore.hgetall(key)  # {'field-1': 'value-1', 'field-2': 'value-2'}

        for field in data:
            rsp_str += CHR_SEP + field + CHR_SEP + data[field]

        return RSP_OK + rsp_str + CHR_EOT


    # HKEYS
    def _OPTS_HKEYS(self, args):
        '''
        Returns all field names in the hash stored at key.
            https://redis.io/commands/hkeys

        MCU → HKEYS#<key>

        MCU ← 100[#<field-1>#<field-2>]@
        '''

        key = args[0]

        fields = self.datastore.keys(key)

        if len(fields) > 0:
            return RSP_OK + CHR_SEP + CHR_SEP.join(fields) + CHR_EOT
        else:
            return RSP_OK + CHR_EOT


    # HVALS
    def _OPTS_HVALS(self, args):
        '''
        Returns all values in the hash stored at key.
            https://redis.io/commands/hvals

        MCU → HVALS#<key>

        MCU ← 100[#<value-1>#<value-2>]@
        '''
        key = args[0]
        values = self.datastore.hvals(key)
        if len(values) > 0:
            return RSP_OK + CHR_SEP + CHR_SEP.join(values) + CHR_EOT
        else:
            return RSP_OK + CHR_EOT


    # HDEL
    def _OPTS_HDEL(self, args):
        '''
        Removes the specified fields from the hash stored at key.
        Specified fields that do not exist within this hash are ignored.
        If key does not exist, it is treated as an empty hash and this command returns 0.
            https://redis.io/commands/hdel

        → HDEL#<key>#<field>[#<field-2>#<field-n>]

        ← 100#<num-of-deleted-keys>@
        '''

        idx = len(args)
        key = args[0]
        fields = args[1:idx]

        num = self.datastore(key, *fields)

        return RSP_OK + CHR_SEP + str(num) + CHR_EOT

    def startTest(self):
        # TEST - SET

        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: SET" + bcolors.ENDC)
        test_cmd = "SET" + CHR_SEP + "set-key" + CHR_SEP + "set-value"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))
        print("LR RSP: " + test_response.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))
        if test_response == RSP_OK + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: GET 1" + bcolors.ENDC)
        test_cmd = "GET" + CHR_SEP + "set-key"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))
        print("LR RSP: " + test_response.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))
        val = self.datastore.get("set-key")

        if test_response == RSP_OK + CHR_SEP + val + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)

        self.datastore.delete("set-key")

        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: GET 2" + bcolors.ENDC)
        test_cmd = "GET" + CHR_SEP + "not-existing-key"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))
        print("LR RSP: " + test_response.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))

        if test_response == ERR_NULL + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: DEL 1" + bcolors.ENDC)
        self._parseCommands("SET" + CHR_SEP + "del-key-1" + CHR_SEP + "del-value-1")
        self._parseCommands("SET" + CHR_SEP + "del-key-2" + CHR_SEP + "del-value-2")

        test_cmd = "DEL" + CHR_SEP + "del-key-1" + CHR_SEP + "del-key-2"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))
        print("LR RSP: " + test_response.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))

        if test_response == RSP_OK + CHR_SEP + "2" + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: DEL 2" + bcolors.ENDC)
        test_cmd = "DEL" + CHR_SEP + "not-existing-key"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))
        print("LR RSP: " + test_response.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))

        if test_response == RSP_OK + CHR_SEP + "0" + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)



        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: KEYS 1" + bcolors.ENDC)

        self._parseCommands("SET" + CHR_SEP + "key-1" + CHR_SEP + "value-1")
        self._parseCommands("SET" + CHR_SEP + "key-2" + CHR_SEP + "value-2")

        test_cmd = "KEYS"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))
        print("LR RSP: " + test_response.replace(CHR_SEP,"#").replace(CHR_EOT,"@"))

        if test_response == RSP_OK + CHR_SEP + "key-2" + CHR_SEP + "key-1" + CHR_EOT or\
                test_response == RSP_OK + CHR_SEP + "key-1" + CHR_SEP + "key-2" + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: KEYS 2" + bcolors.ENDC)

        self._parseCommands("SET" + CHR_SEP + "key-1" + CHR_SEP + "value-1")
        self._parseCommands("SET" + CHR_SEP + "key-2" + CHR_SEP + "value-2")
        self._parseCommands("SET" + CHR_SEP + "other-key" + CHR_SEP + "other-value")

        test_cmd = "KEYS" + CHR_SEP + "key*"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))
        print("LR RSP: " + test_response.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))

        if test_response == RSP_OK + CHR_SEP + "key-2" + CHR_SEP + "key-1" + CHR_EOT or\
                test_response == RSP_OK + CHR_SEP + "key-1" + CHR_SEP + "key-2" + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)

        self.datastore.delete(*["other-key","key-1", "key-2"])

        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: KEYS 3" + bcolors.ENDC)

        test_cmd = "KEYS" + CHR_SEP + "non-existing-key"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))
        print("LR RSP: " + test_response.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))

        if test_response == RSP_OK + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: HSET 1" + bcolors.ENDC)

        test_cmd = "HSET" + CHR_SEP + "hkey-1" + CHR_SEP + "hfield-1" + CHR_SEP + 'hvalue-1'
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))
        print("LR RSP: " + test_response.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))

        if test_response == RSP_HSET_NEW + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: HSET 2" + bcolors.ENDC)

        test_cmd = "HSET" + CHR_SEP + "hkey-1" + CHR_SEP + "hfield-1" + CHR_SEP + 'hvalue-1'
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))
        print("LR RSP: " + test_response.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))

        if test_response == RSP_HSET_UPD + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: HGET" + bcolors.ENDC)

        test_cmd = "HGET" + CHR_SEP + "hkey-1" + CHR_SEP + "hfield-1"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))
        print("LR RSP: " + test_response.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))

        if test_response == RSP_OK + CHR_SEP + "hvalue-1" + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: HGETALL" + bcolors.ENDC)

        self.datastore.hset("hkey-1","hfield-2","hvalue-2")

        test_cmd = "HGETALL" + CHR_SEP + "hkey-1"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))
        print("LR RSP: " + test_response.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))

        if test_response == RSP_OK + CHR_SEP + "hfield-1" + CHR_SEP + "hvalue-1" + CHR_SEP + "hfield-2" + CHR_SEP + "hvalue-2" + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)

        self.datastore.delete("hkey-1")


        print("-----------------------------------------------------------------")
        print(bcolors.BOLD + "TEST: HKEYS" + bcolors.ENDC)

        self.datastore.hset("hkey-1","hfield-2","hvalue-2")

        test_cmd = "HGETALL" + CHR_SEP + "hkey-1"
        test_response = self._parseCommands(test_cmd)
        print("MCU CMD: " + test_cmd.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))
        print("LR RSP: " + test_response.replace(CHR_SEP, "#").replace(CHR_EOT, "@"))

        if test_response == RSP_OK + CHR_SEP + "hfield-1" + CHR_SEP + "hvalue-1" + CHR_SEP + "hfield-2" + CHR_SEP + "hvalue-2" + CHR_EOT:
            print(bcolors.OKBLUE + "PASSED" + bcolors.ENDC)
        else:
            print(bcolors.FAIL + "FAILED" + bcolors.ENDC)

        self.datastore.delete("hkey-1")

        '''
        MCU → HKEYS#<key>

        MCU ← 100[#<field-1>#<field-2>]@
        '''


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

unitTest = SerialManagerUnitTest()
unitTest.startTest()

