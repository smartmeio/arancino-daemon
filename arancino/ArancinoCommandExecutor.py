from arancino.ArancinoCortex import ArancinoComamnd, ArancinoResponse
from arancino.ArancinoConstants import *
import semantic_version as semver
from arancino.ArancinoExceptions import *
from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.ArancinoUtils import ArancinoConfig
from arancino.port.ArancinoPort import PortTypes


class ArancinoCommandExecutor:

    def __init__(self, port_id, port_device, port_type):

        # Port Idientifiers
        self.__port_id = port_id
        self.__port_device = port_device
        self.__port_type = port_type

        # Redis Data Stores
        redis = ArancinoDataStore.Instance()
        self.__datastore = redis.getDataStore()
        self.__devicestore = redis.getDeviceStore()
        self.__datastore_rsvd = redis.getDataStoreRsvd()

        self.__conf = ArancinoConfig.Instance()
        self.__compatibility_array_serial = COMPATIBILITY_MATRIX_MOD_SERIAL
        self.__compatibility_array_test = COMPATIBILITY_MATRIX_MOD_TEST


    def exec(self, arancino_command):
        """
        Exec the Arancino Command and create an Arancino Response.

        :param arancino_command: {ArancinoCommand} The command to execute.
        :return: {ArancinoResponse} The response to send back for the Arancino Command.
        """



        raw_response = None
        response = None

        try:

            if arancino_command is None:
                raise InvalidCommandException("Empty Command Received", ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)

            cmd_id = arancino_command.getId()
            cmd_args = arancino_command.getArguments()


            # retrieve the number of arguments required for the command
            n_args_required = self.__get_args_nr_by_cmd_id(cmd_id)
            n_args = len(cmd_args)

            if n_args_required != n_args:
                raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)



            # START
            if cmd_id == ArancinoCommandIdentifiers.CMD_SYS_START['id']:
                raw_response = self.__OPTS_START(cmd_args)
                return raw_response
            # SET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_SET_STD['id']:
                raw_response = self.__OPTS_SET_STD(cmd_args)
                return raw_response
            # SET PERSISTENT
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_SET_PERS['id']:
                raw_response = self.__OPTS_SET_PERS(cmd_args)
                return raw_response
            # GET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_GET['id']:
                raw_response = self.__OPTS_GET(cmd_args)
                return raw_response
            # DEL
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_DEL['id']:
                raw_response = self.__OPTS_DEL(cmd_args)
                return raw_response
            # KEYS
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_KEYS['id']:
                raw_response = self.__OPTS_KEYS(cmd_args)
                return raw_response
            # HSET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HSET['id']:
                raw_response = self.__OPTS_HSET(cmd_args)
                return raw_response
            # HGET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HGET['id']:
                raw_response = self.__OPTS_HGET(cmd_args)
                return raw_response
            # HGETALL
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HGETALL['id']:
                raw_response = self.__OPTS_HGETALL(cmd_args)
                return raw_response
            # HKEYS
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HKEYS['id']:
                raw_response = self.__OPTS_HKEYS(cmd_args)
                return raw_response
            # HVALS
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HVALS['id']:
                raw_response = self.__OPTS_HVALS(cmd_args)
                return raw_response
            # HDEL
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HDEL['id']:
                raw_response = self.__OPTS_HDEL(cmd_args)
                return raw_response
            # PUB
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_PUB['id']:
                raw_response = self.__OPTS_PUB(cmd_args)
                return raw_response
            # FLUSH
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_FLUSH['id']:
                raw_response = self.__OPTS_FLUSH(cmd_args)
                return raw_response
            # Default
            else:
                # TODO better a new Error code, something like ERR_CMD_NOT_IMPL: becouse if there, the was fount in
                #   the list, but there are not OPTS to be executed, so the OPTS is not implemented
                raw_response = ArancinoCommandErrorCodes.ERR_CMD_NOT_FND + ArancinoSpecialChars.CHR_SEP
                return raw_response
            #cmd = ArancinoComamnd(cmd_id=cmd_id, cmd_args=cmd_args)
            #response = ArancinoResponse(raw_response=raw_response)

        except ArancinoException as ex:
            raise ex

        except Exception as ex:
            raise ex


    # START
    def __OPTS_START(self, args):
        """
        Microcontroller sends START command to start communication

        MCU → START@

        MCU ← 100@ (OK)
        """

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:

            # first argument in the START comamnd is the version of the library
            value_libvers = args[0]
            key_libvers = ArancinoReservedChars.RSVD_KEY_LIBVERSION + self.__port_id + ArancinoReservedChars.RSVD_CHARS

            # convert
            semver_value_libvers = semver.Version(value_libvers)

            # store the reserved key
            # self.__datastore.set(key_libvers, value_libvers)

            # and then check if it's compatible. if the library is not compatible, disconnect the board and
            # if value_libvers not in self.compatibility_array:
            #     # TODO disconnect the device. If the device is not disconnected, it will try to START every 2,5 seconds.
            #     raise NonCompatibilityException("Module version " + conf.version + " can not work with Library version " + value_libvers + " on the device: " + self.arancino.port.device + " - " + self.arancino.id, const.ERR_NON_COMPATIBILITY)
            # else:
            #     return const.RSP_OK + const.CHR_EOT

            # if library version is >= of v (one at least) then compatibility is ok
            # eg1: compatibility_array = ["1.*.*", "2.1.*"] and value_libevers = "1.0.0"
            # "1.0.0" >= "2.1.*" ---> False (KO: go foward)
            # "1.0.0" >= "1.*.*" ---> True (OK: can return)
            #
            #
            # eg3: compatibility_array = ["0.1.*", "0.2.*"] and value_libevers = "1.0.0"
            # "1.0.0" >= "0.1.*" ---> False (KO: go forward)
            # "1.0.0" >= "0.2.*" ---> False (KO: go forward and raise exception)

            compatibility_array = {}

            if self.__port_type == PortTypes.SERIAL:
                compatibility_array = self.__compatibility_array_serial
            elif self.__port_type == PortTypes.TEST:
                compatibility_array = self.__compatibility_array_test


            for compatible_ver in compatibility_array:
                semver_compatible_ver = semver.SimpleSpec(compatible_ver)
                if semver_value_libvers in semver_compatible_ver:
                    return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

            # TODO disconnect the device. If the device is not disconnected, it will try to START every 2,5 seconds.
            raise NonCompatibilityException(
                "Module version " + str(self.__conf.get_metadata_version()) + " can not work with Library version " + value_libvers + " on the device: " + self.__port_device + " - " + self.__port_id,
                ArancinoCommandErrorCodes.ERR_NON_COMPATIBILITY)

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_SYS_START['id'] + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # SET STANDARD (to standard device store)
    def __OPTS_SET_STD(self, args):
        # wraps __OPTS_SET
        return self.__OPTS_SET(args, "STD")

    # SET PERSISTENT (to persistent keys device store)
    def __OPTS_SET_PERS(self, args, ):
        # wraps __OPTS_SET
        return self.__OPTS_SET(args, "PERS")

    # SET
    def __OPTS_SET(self, args, type):
        '''
        Set key to hold the string value. If key already holds a value,
        it is overwritten, regardless of its type. Any previous time to live
        associated with the key is discarded on successful SET operation.
            https://redis.io/commands/set

        MCU → SET#<key>#<value>@

        MCU ← 100@ (OK)
        MCU ← 202@ (KO)
        MCU ← 206@ (KO)
        MCU ← 207@ (KO)
        MCU ← 208@ (KO)
        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            value = args[1]
            rsp = False

            try:
                # Keys must be unique among data stores

                # STANDARD DATA STORE (even with reserved key by arancino)
                if type == 'STD':

                    # check if key exist in other data store
                    if (self.__datastore_rsvd.exists(key) == 1):
                        raise RedisStandardKeyExistsInPersistentDatastoreException(
                            "Duplicate Key In Persistent Data Store: ", ArancinoCommandErrorCodes.ERR_REDIS_KEY_EXISTS_IN_PERS)
                    else:
                        # store the value at key
                        rsp = self.__datastore.set(key, value)


                else:
                    # PERSISTENT DATA STORE
                    if type == 'PERS':

                        # check if key exist in other data store
                        if (self.__datastore.exists(key) == 1):
                            raise RedisPersistentKeyExistsInStadardDatastoreException(
                                "Duplicate Key In Standard Data Store: ", ArancinoCommandErrorCodes.ERR_REDIS_KEY_EXISTS_IN_STD)
                        else:
                            # write to the dedicate data store (dedicated to persistent keys)
                            rsp = self.__datastore_rsvd.set(key, value)

                if rsp:
                    # return ok response
                    return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT
                else:
                    # return the error code
                    return ArancinoSpecialChars.ERR_SET + ArancinoSpecialChars.CHR_EOT

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            # try:

            #     # STANDARD DATA STORE (even with reserved key by arancino)
            #     if type == 'STD':

            #         # if it's the reserverd key __LIBVERSION__,
            #         # then add port id to associate the device and the running version of the library
            #         if key.upper() == const.RSVD_KEY_LIBVERSION:
            #             key += self.arancino.id + const.RSVD_CHARS

            #         # check if key exist in the other data store
            #         exist = self.datastore_rsvd.exists(key)
            #         if( exist == 1):
            #             raise RedisGenericException("Duplicate Key In Persistent Data Store: ", const.ERR_REDIS_KEY_EXISTS_IN_PERS)
            #         else:
            #             rsp = self.datastore.set(key, value)

            #     # PERSISTENT DATA STORE
            #     else:
            #         if type == 'PERS':

            #             # check if key exist in the other data store
            #             exist = self.datastore.exists(key)
            #             if( exist == 1):
            #                 raise RedisGenericException("Duplicate Key In Standard Data Store: ", const.ERR_REDIS_KEY_EXISTS_IN_STD)
            #             else:
            #                 # write to the dedicate data store (dedicated to persistent keys)
            #                 rsp = self.datastore_rsvd.set(key, value)

            # except Exception as ex:
            #     raise RedisGenericException("Redis Error: " + str(ex), const.ERR_REDIS)

            # if rsp:
            #     # return ok response
            #     return const.RSP_OK + const.CHR_EOT
            # else:
            #     # return the error code
            #     return const.ERR_SET + const.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_SET['id'] + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # GET
    def __OPTS_GET(self, args):
        '''
        Get the value of key. If the key does not exist the special value nil is returned.
        An error is returned if the value stored at key is not a string,
        because GET only handles string values.
            https://redis.io/commands/get

        MCU → GET#<key>@

        MCU ← 100#<value>@ (OK)
        MCU ← 201@ (KO)
        '''

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            rsp = None

            try:
                '''
                # It's a reserved key.
                if key.startswith(const.RSVD_CHARS) and key.endswith(const.RSVD_CHARS):

                    # if it's the reserverd key __LIBVERSION__,
                    # then add port id to associate the device and the running version of the library
                    if key.upper() == const.RSVD_KEY_LIBVERSION:
                        key += self.arancino.id + const.RSVD_CHARS

                    rsp = self.datastore_rsvd.get(key)

                # It's an application key.
                else:
                    rsp = self.datastore.get(key)
                '''
                # if it's the reserverd key __LIBVERSION__,
                # then add port id to associate the device and the running version of the library
                if key.upper() == ArancinoReservedChars.RSVD_KEY_LIBVERSION:
                    key += self.__port_id + ArancinoReservedChars.RSVD_CHARS

                # first get from standard datastore
                rsp = self.__datastore.get(key)

                # then try get from reserved datastore
                if rsp is None:
                    rsp = self.__datastore_rsvd.get(key)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            if rsp is not None:
                # return the value
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(rsp) + ArancinoSpecialChars.CHR_EOT
            else:
                # return the error code
                return ArancinoCommandErrorCodes.ERR_NULL + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_GET['id'] + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # DEL
    def __OPTS_DEL(self, args):
        '''
        Removes the specified keys. A key is ignored if it does not exist.
            https://redis.io/commands/del

        MCU → DEL#<key-1>[#<key-2>#<key-n>]@

        MCU ← 100#<num-of-deleted-keys>@
        '''

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received >= n_args_required:

            try:

                # TODO delete user-reserved keys

                num = self.__datastore.delete(*args)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(num) + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_DEL['id'] + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # KEYS
    def __OPTS_KEYS(self, args):
        '''
        Returns all keys matching pattern.
            https://redis.io/commands/keys

        MCU → KEYS[#<pattern>]@

        MCU ← 100[#<key-1>#<key-2>#<key-n>]@
        '''

        if len(args) == 0:
            pattern = '*'  # w/o pattern
        else:
            pattern = args[0]  # w/ pattern

        try:

            keys = self.__datastore.keys(pattern)
            keys_pers = self.__datastore_rsvd.keys(pattern)

            keys = keys + keys_pers

        except Exception as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        if len(keys) > 0:

            ### uncomment below to apply a filter to exclude reserved keys from returned array

            keys_filtered = []

            for val in keys:
                if not (val.startswith(ArancinoReservedChars.RSVD_CHARS) and val.endswith(ArancinoReservedChars.RSVD_CHARS)):
                    keys_filtered.append(val)

            if len(keys_filtered) > 0:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + ArancinoSpecialChars.CHR_SEP.join(keys_filtered) + ArancinoSpecialChars.CHR_EOT

            else:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

            ### comment the following line when apply the patch above (exclude reserved keys)
            # return const.RSP_OK + const.CHR_SEP + const.CHR_SEP.join(keys) + const.CHR_EOT

        else:
            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

    # HSET
    def __OPTS_HSET(self, args):
        '''
        Sets field in the hash stored at key to value.
        If key does not exist, a new key holding a hash is created.
        If field already exists in the hash, it is overwritten.
            https://redis.io/commands/hset

        MCU → HSET#<key>#<field>#<value>@

        MCU ← 101@
        MCU ← 102@
        '''

        n_args_required = 3
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            field = args[1]
            value = args[2]

            try:

                rsp = self.__datastore.hset(key, field, value)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            if rsp == 1:
                return ArancinoCommandResponseCodes.RSP_HSET_NEW + ArancinoSpecialChars.CHR_EOT
            else:  # 0
                return ArancinoCommandResponseCodes.RSP_HSET_UPD + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_HSET['id'] + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # HGET
    def __OPTS_HGET(self, args):
        '''
        Returns the value associated with field in the hash stored at key.
            https://redis.io/commands/hget

        MCU → HGET#<key>#<field>@

        MCU ← 100#<value>@
        MCU ← 201@

        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]
            field = args[1]

            try:

                value = self.__datastore.hget(key, field)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            if value is not None:
                # return the value
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(value) + ArancinoSpecialChars.CHR_EOT
            else:
                # return the error code
                return ArancinoCommandErrorCodes.ERR_NULL + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_HGET['id'] + ". Found: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # HGETALL
    def __OPTS_HGETALL(self, args):

        '''
        Returns all fields and values of the hash stored at key.
        In the returned value, every field name is followed by its value,
        so the length of the reply is twice the size of the hash.
            https://redis.io/commands/hgetall

        MCU → HGETALL#<key>@

        MCU ← 100[#<field-1>#<value-1>#<field-2>#<value-2>]@
        '''

        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]

            rsp_str = ""

            try:

                data = self.__datastore.hgetall(key)  # {'field-1': 'value-1', 'field-2': 'value-2'}

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            for field in data:
                rsp_str += ArancinoSpecialChars.CHR_SEP + field + ArancinoSpecialChars.CHR_SEP + data[field]

            return ArancinoCommandResponseCodes.RSP_OK + rsp_str + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_HGETALL['id'] + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # HKEYS
    def __OPTS_HKEYS(self, args):

        '''
        Returns all field names in the hash stored at key.
            https://redis.io/commands/hkeys

        MCU → HKEYS#<key>@

        MCU ← 100[#<field-1>#<field-2>]@
        '''
        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:

            key = args[0]

            try:

                fields = self.__datastore.hkeys(key)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            if len(fields) > 0:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + ArancinoSpecialChars.CHR_SEP.join(fields) + ArancinoSpecialChars.CHR_EOT
            else:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_HKEYS['id'] + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # HVALS
    def __OPTS_HVALS(self, args):
        '''
        Returns all values in the hash stored at key.
            https://redis.io/commands/hvals

        MCU → HVALS#<key>

        MCU ← 100[#<value-1>#<value-2>]@
        '''
        n_args_required = 1
        n_args_received = len(args)

        if n_args_received == n_args_required:
            key = args[0]

            try:

                values = self.__datastore.hvals(key)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            if len(values) > 0:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + ArancinoSpecialChars.CHR_SEP.join(values) + ArancinoSpecialChars.CHR_EOT
            else:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_HVALS['id'] + ". Received: " + str(
                    n_args_received) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # HDEL
    def __OPTS_HDEL(self, args):
        '''
        Removes the specified fields from the hash stored at key.
        Specified fields that do not exist within this hash are ignored.
        If key does not exist, it is treated as an empty hash and this command returns 0.
            https://redis.io/commands/hdel

        MCU → HDEL#<key>#<field>[#<field-2>#<field-n>]@

        MCU ← 100#<num-of-deleted-keys>@
        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received >= n_args_required:
            idx = len(args)
            key = args[0]
            fields = args[1:idx]

            try:

                num = self.__datastore.hdel(key, *fields)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(num) + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_HDEL['id'] + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

    # PUB
    def __OPTS_PUB(self, args):
        '''
        Posts a message to the given channel. Return the number of clients
        that received the message.
            https://redis.io/commands/publish

        MCU → PUB#<channel>#<message>@

        MCU ← 100#<num-of-reached-clients>@
        '''

        n_args_required = 2
        n_args_received = len(args)

        if n_args_received >= n_args_required:
            channel = args[0]
            message = args[1]

            try:

                num = self.datastore.publish(channel, message)

            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandResponseCodes.ERR_REDIS)

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(num) + ArancinoSpecialChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_PUB['id'] + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", ArancinoCommandResponseCodes.ERR_CMD_PRM_NUM)

    # FLUSH
    def __OPTS_FLUSH(self, args):
        '''
        Delete all the keys of the currently application DB.
        This command never fails.
            https://redis.io/commands/flushdb

        MCU → FLUSH@

        MCU ← 100@
        '''

        n_args_required = 0
        n_args_received = len(args)

        if n_args_received >= n_args_required:

            try:

                # before flush, save all Reserved Keys
                rsvd_keys = self.__datastore.keys(ArancinoReservedChars.RSVD_CHARS + "*" + ArancinoReservedChars.RSVD_CHARS)
                rsvd_keys_value = {}
                for k in rsvd_keys:
                    rsvd_keys_value[k] = self.__datastore.get(k)

                # flush
                # Andrea comment
                # rsp = self.datastore.flushdb()

                # finally set them all again
                for k, v in rsvd_keys_value.items():
                    self.__datastore.set(k, v)

                # flush directly the datastore; reserved keys are stored separately
                # rsp = self.datastore.flushdb()


            except Exception as ex:
                raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoReservedChars.CHR_EOT

        else:
            raise InvalidArgumentsNumberException(
                "Invalid arguments number for command " + ArancinoCommandIdentifiers.CMD_APP_FLUSH['id'] + ". Received: " + str(
                    n_args_received) + "; Minimum Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)


    def __get_args_nr_by_cmd_id(self, cmd_id):
        '''
        Get the number of Argument for the specified Command Identifier.

        :param cmd_id: {String} the Command identifier.
        :return: {Integer} the number of arguments for the specified Command Identifier.
        '''

        command = ArancinoCommandIdentifiers.COMMANDS_DICT[cmd_id]
        num = command["args"]

        return num
