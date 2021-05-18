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
import decimal

from redis import RedisError

from arancino.ArancinoConstants import *
import semantic_version as semver

from arancino.ArancinoCortex import ArancinoResponse
from arancino.ArancinoExceptions import *
from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.utils.ArancinoUtils import ArancinoConfig
from arancino.port.ArancinoPort import PortTypes
from datetime import datetime


class ArancinoCommandExecutor:

    def __init__(self, port_id, port_device, port_type):

        # Port Identifiers
        self.__port_id = port_id
        self.__port_device = port_device
        self.__port_type = port_type

        # Redis Data Stores
        redis = ArancinoDataStore.Instance()
        self.__datastore = redis.getDataStoreStd()
        self.__datastore_rsvd = redis.getDataStoreRsvd()
        self.__devicestore = redis.getDataStoreDev()
        self.__datastore_pers = redis.getDataStorePer()
        self.__datastore_tser = redis.getDataStoreTse()
        self.__datastore_tag = redis.getDataStoreTag()

        self.__conf = ArancinoConfig.Instance()
#        self.__compatibility_array_serial = COMPATIBILITY_MATRIX_MOD_SERIAL[str(self.__conf.get_metadata_version().truncate())]
#        self.__compatibility_array_test = COMPATIBILITY_MATRIX_MOD_TEST[str(self.__conf.get_metadata_version().truncate())]


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
            # n_args_required = self.__get_args_nr_by_cmd_id(cmd_id)
            # n_args = len(cmd_args)
            #
            # if n_args_required != n_args:
            #     raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)


            #region Options
            # START
            if cmd_id == ArancinoCommandIdentifiers.CMD_SYS_START['id']:
                raw_response = self.__OPTS_START(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # SET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_SET_STD['id']:
                raw_response = self.__OPTS_SET_STD(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # SET PERSISTENT
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_SET_PERS['id']:
                raw_response = self.__OPTS_SET_PERS(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # GET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_GET['id']:
                raw_response = self.__OPTS_GET(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # GET RSVD
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_GET_RSVD['id']:
                raw_response = self.__OPTS_GET_RSVD(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # DEL
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_DEL['id']:
                raw_response = self.__OPTS_DEL(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # KEYS
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_KEYS['id']:
                raw_response = self.__OPTS_KEYS(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # HSET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HSET_STD['id']:
                raw_response = self.__OPTS_HSET_STD(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # HSET PERSISTENT
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HSET_PERS['id']:
                raw_response = self.__OPTS_HSET_PERS(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # HGET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HGET['id']:
                raw_response = self.__OPTS_HGET(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # HGETALL
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HGETALL['id']:
                raw_response = self.__OPTS_HGETALL(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # HKEYS
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HKEYS['id']:
                raw_response = self.__OPTS_HKEYS(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # HVALS
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HVALS['id']:
                raw_response = self.__OPTS_HVALS(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # HDEL
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_HDEL['id']:
                raw_response = self.__OPTS_HDEL(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # PUB
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_PUB['id']:
                raw_response = self.__OPTS_PUB(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # FLUSH
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_FLUSH['id']:
                raw_response = self.__OPTS_FLUSH(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # MSET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_MSET_STD['id']:
                raw_response = self.__OPTS_MSET_STD(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # MSET PERSISTENT
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_MSET_PERS['id']:
                raw_response = self.__OPTS_MSET_PERS(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # MGET
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_MGET['id']:
                raw_response = self.__OPTS_MGET(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # STORE
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_STORE['id']:
                raw_response = self.__OPTS_STORE(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # STORETAGS
            elif cmd_id == ArancinoCommandIdentifiers.CMD_APP_STORETAGS['id']:
                raw_response = self.__OPTS_STORETAGS(cmd_args)
                return ArancinoResponse(raw_response=raw_response)
            # Default
            else:
                raw_response = ArancinoCommandErrorCodes.ERR_CMD_NOT_FND + ArancinoSpecialChars.CHR_SEP
                return ArancinoResponse(raw_response=raw_response)

            # endregion
            #cmd = ArancinoComamnd(cmd_id=cmd_id, cmd_args=cmd_args)
            #response = ArancinoResponse(raw_response=raw_response)

        except ArancinoException as ex:
            raise ex

        except Exception as ex:
            raise ex

    #region COMMANDS OPTIONS

    #region START
    def __OPTS_START(self, args):
        """
        Microcontroller sends START command to start communication

        MCU → START@

        MCU ← 100@ (OK)
        """

        # first argument in the START comamnd is the version of the library
#        value_libvers = args[0]

        # convert string to semver object
#        semver_value_libvers = semver.Version(value_libvers)

        # and then check if it's compatible. if the library is not compatible, disconnect the board and
        # if value_libvers not in self.compatibility_array:
        #     # NOTE: If the device is not disconnected, it will try to START every 2,5 seconds.
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

#        compatibility_array = {}

#        if self.__port_type == PortTypes.SERIAL:
#            compatibility_array = self.__compatibility_array_serial
#        elif self.__port_type == PortTypes.TEST:
#            compatibility_array = self.__compatibility_array_test


        # for compatible_ver in compatibility_array:
        #     semver_compatible_ver = semver.SimpleSpec(compatible_ver)
        #     if semver_value_libvers in semver_compatible_ver:
        #         #now = datetime.now()
        #         #ts = datetime.timestamp(now)
        #         ts = datetime.now().timestamp()

        ts = str(int(datetime.now().timestamp() * 1000))
        return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + self.__port_id + ArancinoSpecialChars.CHR_SEP + str(ts) + ArancinoSpecialChars.CHR_EOT

        # NOTE: If the device is not disconnected, it will try to START every 2,5 seconds.
#        raise NonCompatibilityException(
#            "Module version " + str(self.__conf.get_metadata_version()) + " can not work with Library version " + value_libvers,
#            ArancinoCommandErrorCodes.ERR_NON_COMPATIBILITY)

    #endregion

    #region SET
    #region SET STANDARD (to standard device store)
    def __OPTS_SET_STD(self, args):
        # wraps __OPTS_SET
        return self.__OPTS_SET(args, self.__datastore, self.__datastore_pers, "STD")
    # endregion

    #region SET PERSISTENT (to persistent keys device store)
    def __OPTS_SET_PERS(self, args ):
        # wraps __OPTS_SET
        return self.__OPTS_SET(args, self.__datastore_pers, self.__datastore, "PERS")
    # endregion

    #region SET
    def __OPTS_SET(self, args, first_datastore, second_datastore, type):
        '''
        Set key to hold the string value. If key already holds a value,
        it is overwritten, regardless of its type. Any previous time to live
        associated with the key is discarded on successful SET operation.
            https://redis.io/commands/set

        If type → 'STD' → first_datastore is volatile datastore and second_datastore is persistent datastore
        If type → 'PERS' → first_datastore is persistent datastore and second_datastore is volatile datastore

        MCU → SET#<key>#<value>@

        MCU ← 100@ (OK)
        MCU ← 202@ (KO)
        MCU ← 206@ (KO)
        MCU ← 207@ (KO)
        MCU ← 208@ (KO)
        '''


        key = args[0]
        value = args[1]
        rsp = False

        try:
            # Keys must be unique among data stores

            # check if key exist in other data store
            if (second_datastore.exists(key) == 1):
                if type == 'STD':
                    raise RedisStandardKeyExistsInPersistentDatastoreException("Duplicate Key In Persistent Data Store: ", ArancinoCommandErrorCodes.ERR_REDIS_KEY_EXISTS_IN_PERS)
                if type == 'PERS':
                    raise RedisPersistentKeyExistsInStadardDatastoreException("Duplicate Key In Standard Data Store: ", ArancinoCommandErrorCodes.ERR_REDIS_KEY_EXISTS_IN_STD)
            else:
                # store the value at key
                rsp = first_datastore.set(key, value)

            if rsp:
                # return ok response
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT
            else:
                # return the error code
                return ArancinoSpecialChars.ERR_SET + ArancinoSpecialChars.CHR_EOT


        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except ArancinoException as ex:
            raise ex

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion
    # region SET RSVD
    def __OPTS_SET_RSVD(self, args):


        key = args[0]
        value = args[1]
        rsp = False

        try:

            if key in ArancinoReservedChars:

                rsp = self.__datastore_rsvd.set(key, value)

                if rsp:
                    # return ok response
                    return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT
                else:
                    # return the error code
                    return ArancinoSpecialChars.ERR_SET + ArancinoSpecialChars.CHR_EOT
            else:
                raise ArancinoException("Generic Error: Reserved Keys Not Exists", ArancinoCommandErrorCodes.ERR)


        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except ArancinoException as ex:
            raise ex

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)
    # endregion
    # endregion

    #region GET
    def __OPTS_GET(self, args):
        '''
        Get the value of key. If the key does not exist the special value nil is returned.
        An error is returned if the value stored at key is not a string,
        because GET only handles string values.
            https://redis.io/commands/get

        MCU → GET#<key>@

        MCU ← 100#<value>@ (OK)
        MCU ← 200@ (KO) - Generic Error
        MCU ← 206@ (KO) - Redis Error
        '''


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
            ''' # DEPRECATED
            if key.upper() == ArancinoReservedChars.RSVD_KEY_LIBVERSION:
                key += self.__port_id + ArancinoReservedChars.RSVD_CHARS
            '''

            # first get from standard datastore
            rsp = self.__datastore.get(key)

            # then try get from reserved datastore
            if rsp is None:
                rsp = self.__datastore_pers.get(key)

            # check again, if None send back Null Value.
            if rsp is None:
                rsp = ArancinoSpecialChars.CHR_NULL_VALUE

            # return the value
            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + rsp + ArancinoSpecialChars.CHR_EOT


        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    # region GET RSVD
    def __OPTS_GET_RSVD(self, args):
        '''
        Get the value of reseved key. If the key does not exist the special value nil is returned.
        An error is returned if the value stored at key is not a string,
        because GET only handles string values.
            https://redis.io/commands/get

        MCU → GET#<key>@

        MCU ← 100#<value>@ (OK)
        MCU ← 200@ (KO) - Generic Error
        MCU ← 206@ (KO) - Redis Error
        '''

        key = args[0]
        rsp = None

        try:

            # first get from reserved datastore
            rsp = self.__datastore_rsvd.get(key)

            if rsp is None:
                rsp = ArancinoSpecialChars.CHR_NULL_VALUE

            # return the value
            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + rsp + ArancinoSpecialChars.CHR_EOT


        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    #region DEL
    def __OPTS_DEL(self, args):
        '''
        Removes the specified keys. A key is ignored if it does not exist.
            https://redis.io/commands/del

        MCU → DEL#<key-1>[#<key-2>#<key-n>]@

        MCU ← 100#<num-of-deleted-keys>@
        '''

        try:

            key = args[0]

            num = self.__datastore.delete(key)

            # then try to delete key in the persistent datastore
            if num == 0:
                num = self.__datastore_pers.delete(key)

            # then try to delete key in the time series datastore
            if num == 0:

                key = "{}*".format(key)
                keys = self.__datastore_tser.redis.keys(key)
                if len(keys) > 0:
                    num = self.__datastore_tser.redis.delete(*keys)

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(num) + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)
    # endregion

    #region KEYS
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
            keys_pers = self.__datastore_pers.keys(pattern)

            keys = keys + keys_pers

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

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    # region HSET
    # region HSET STD
    def __OPTS_HSET_STD(self, args):
        return self.__OPTS_HSET(args, self.__datastore, self.__datastore_pers, "STD")
    # endregion

    # region HSET PERS
    def __OPTS_HSET_PERS(self, args):
        return self.__OPTS_HSET(args, self.__datastore_pers, self.__datastore, "PERS")
    # endregion

    # region HSET
    def __OPTS_HSET(self, args, first_datastore, second_datastore, type):
        '''
        Sets field in the hash stored at key to value.
        If key does not exist, a new key holding a hash is created.
        If field already exists in the hash, it is overwritten.
            https://redis.io/commands/hset

        MCU → HSET#<key>#<field>#<value>@

        MCU ← 101@
        MCU ← 102@
        '''


        key = args[0]
        field = args[1]
        value = args[2]
        rsp = None

        try:

            # Keys must be unique among data stores

            # check if key exist in other data store
            if (second_datastore.exists(key) == 1):
                if type == 'STD':
                    raise RedisStandardKeyExistsInPersistentDatastoreException("Duplicate Key In Persistent Data Store: ", ArancinoCommandErrorCodes.ERR_REDIS_KEY_EXISTS_IN_PERS)
                if type == 'PERS':
                    raise RedisPersistentKeyExistsInStadardDatastoreException("Duplicate Key In Standard Data Store: ", ArancinoCommandErrorCodes.ERR_REDIS_KEY_EXISTS_IN_STD)
            else:
                # store the value at key and field
                rsp = first_datastore.hset(key, field, value)


            if rsp is not None:
                if rsp == 1:
                    return ArancinoCommandResponseCodes.RSP_HSET_NEW + ArancinoSpecialChars.CHR_EOT
                else:  # 0
                    return ArancinoCommandResponseCodes.RSP_HSET_UPD + ArancinoSpecialChars.CHR_EOT
            else:
                # return the error code
                return ArancinoSpecialChars.ERR_SET + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except ArancinoException as ex:
            raise ex

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion
    # endregion

    #region HGET
    def __OPTS_HGET(self, args):
        '''
        Returns the value associated with field in the hash stored at key.
            https://redis.io/commands/hget

        MCU → HGET#<key>#<field>@

        MCU ← 100#<value>@
        MCU ← 200@ (KO) - Generic Error
        MCU ← 206@ (KO) - Redis Error

        '''

        key = args[0]
        field = args[1]
        rsp = None

        try:

            # first get from standard datastore
            rsp = self.__datastore.hget(key, field)

            # then try get from reserved datastore
            if rsp is None:
                rsp = self.__datastore_pers.hget(key, field)

            # check again, if None send back Null Value.
            if rsp is None:
                rsp = ArancinoSpecialChars.CHR_NULL_VALUE

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + rsp + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    #region HGETALL
    def __OPTS_HGETALL(self, args):

        '''
        Returns all fields and values of the hash stored at key.
        In the returned value, every field name is followed by its value,
        so the length of the reply is twice the size of the hash.
            https://redis.io/commands/hgetall

        MCU → HGETALL#<key>@

        MCU ← 100[#<field-1>#<value-1>#<field-2>#<value-2>]@
        MCU ← 200@ (KO) - Generic Error
        MCU ← 206@ (KO) - Redis Error
        '''


        key = args[0]
        rsp_str = ""

        try:

            data = self.__datastore.hgetall(key)  # {'field-1': 'value-1', 'field-2': 'value-2'}

            # empty data, check in persistent datastore
            if not bool(data):
                data = self.__datastore_pers.hgetall(key)

            for field in data:
                rsp_str += ArancinoSpecialChars.CHR_SEP + field + ArancinoSpecialChars.CHR_SEP + data[field]

            return ArancinoCommandResponseCodes.RSP_OK + rsp_str + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    #region HKEYS
    def __OPTS_HKEYS(self, args):
        '''
        Returns all field names in the hash stored at key.
            https://redis.io/commands/hkeys

        MCU → HKEYS#<key>@

        MCU ← 100[#<field-1>#<field-2>]@
        MCU ← 200@ (KO) - Generic Error
        MCU ← 206@ (KO) - Redis Error
        '''

        key = args[0]
        fields = []

        try:

            fields = self.__datastore.hkeys(key)

            if len(fields) == 0:
                # empty data, check in persistent datastore
                fields = self.__datastore_pers.hkeys(key)

            if len(fields) > 0:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + ArancinoSpecialChars.CHR_SEP.join(fields) + ArancinoSpecialChars.CHR_EOT
            else:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)
    # endregion

    #region HVALS
    def __OPTS_HVALS(self, args):
        '''
        Returns all values in the hash stored at key.
            https://redis.io/commands/hvals

        MCU → HVALS#<key>

        MCU ← 100[#<value-1>#<value-2>]@
        MCU ← 200@ (KO) - Generic Error
        MCU ← 206@ (KO) - Redis Error
        '''

        key = args[0]
        values = []
        try:

            values = self.__datastore.hvals(key)

            if len(values) == 0:
                # empty data, check in persistent datastore
                values = self.__datastore_pers.hvals(key)

            if len(values) > 0:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + ArancinoSpecialChars.CHR_SEP.join(values) + ArancinoSpecialChars.CHR_EOT
            else:
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    #region HDEL
    def __OPTS_HDEL(self, args):
        '''
        Removes the specified fields from the hash stored at key.
        Specified fields that do not exist within this hash are ignored.
        If key does not exist, it is treated as an empty hash and this command returns 0.
            https://redis.io/commands/hdel

        MCU → HDEL#<key>#<field>[#<field-2>#<field-n>]@

        MCU ← 100#<num-of-deleted-keys>@
        '''

        idx = len(args)
        key = args[0]
        fields = args[1:idx]

        try:

            num = self.__datastore.hdel(key, *fields)

            # then try get from reserved datastore
            if num == 0:
                num = self.__datastore_pers.delete(*fields)

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(num) + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    #region PUB
    def __OPTS_PUB(self, args):
        '''
        Posts a message to the given channel. Return the number of clients
        that received the message.
            https://redis.io/commands/publish

        MCU → PUB#<channel>#<message>@

        MCU ← 100#<num-of-reached-clients>@
        '''

        channel = args[0]
        message = args[1]

        try:

            num = self.__datastore.publish(channel, message)

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(num) + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)
    # endregion

    #region FLUSH
    def __OPTS_FLUSH(self, args):
        '''
        Delete all the keys of the currently application DB.
        This command never fails.
            https://redis.io/commands/flushdb

        MCU → FLUSH@

        MCU ← 100@
        '''

        try:

            # before flush, save all Reserved Keys
            rsvd_keys = self.__datastore.keys(ArancinoReservedChars.RSVD_CHARS + "*" + ArancinoReservedChars.RSVD_CHARS)
            rsvd_keys_value = {}
            for k in rsvd_keys:
                rsvd_keys_value[k] = self.__datastore.get(k)

            # flush
            rsp = self.__datastore.flushdb()
            rsp = self.__datastore_pers.flushdb()

            # finally set them all again
            for k, v in rsvd_keys_value.items():
                self.__datastore.set(k, v)

            # flush directly the datastore; reserved keys are stored separately
            # rsp = self.datastore.flushdb()

            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)
    # endregion

    # region MSET

    # region MSET STD
    def __OPTS_MSET_STD(self, args):
        # wraps __OPTS_MSET
        return self.__OPTS_MSET(args, self.__datastore)
    # endregion

    # region MSET PERS
    def __OPTS_MSET_PERS(self, args):
        # wraps __OPTS_MSET
        return self.__OPTS_MSET(args, self.__datastore_pers)
    # endregion

    # region MSET
    def __OPTS_MSET(self, args, datastore):
        '''
        Sets the given keys to their respective values. MSET replaces existing values with new values, just as regular SET.
            https://redis.io/commands/mset

        MCU → MSET#<key1>%<key2>%<key3>#<value1>%<value2>%<value3>@

        MCU ← 100@
        MCU ← 200@

        No check if one or all the keys exist in other datastores.

        '''

        keys = args[0]
        values = args[1]

        try:

            keys_array = keys.split(ArancinoSpecialChars.CHR_ARR_SEP)
            values_array = values.split(ArancinoSpecialChars.CHR_ARR_SEP)

            if keys_array and values_array and len(keys_array) > 0 and len(values_array) and len(keys_array) == len(values_array):

                # create a map of key-value
                map = {}
                for idx, key in enumerate(keys_array):
                    map[key] = values_array[idx]

                value = datastore.mset(map)
            else:
                raise ArancinoException("Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty", ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)

            if value:
                # return ok
                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT
            else:
                # return the error code
                return ArancinoCommandErrorCodes.ERR_NULL + ArancinoSpecialChars.CHR_EOT


        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)


    # endregion
    # endregion

    #region MGET
    def __OPTS_MGET(self, args):
        '''
        Sets the given keys to their respective values. MSET replaces existing values with new values, just as regular SET.
            https://redis.io/commands/mset

        MCU → MGET#<key1>%<key2>%<key3>@

        MCU ← 100#<value1>%<value2>%<value3>@
        MCU ← 200@ (KO) - Generic Error
        MCU ← 201@ (KO) - Null Error
        MCU ← 206@ (KO) - Redis Error

        '''

        keys = args[0]
        values = []

        try:

            keys_array = keys.strip().split(ArancinoSpecialChars.CHR_ARR_SEP)

            if keys_array and len(keys_array) > 0:

                values = self.__datastore.mget(keys_array)

            else:
                raise ArancinoException("Arguments Error: Arguments are incorrect or empty. Please check if number of Keys are the same of number of Values, or check if they are not empty", ArancinoCommandErrorCodes.ERR_INVALID_ARGUMENTS)


            if values:

                for idx, val in enumerate(values):
                    if val is None:

                        # check if key exists in persistent datastore:
                        chk = self.__datastore_pers.get(keys_array[idx])

                        if chk is None:
                            values[idx] = ArancinoSpecialChars.CHR_NULL_VALUE
                        else:
                            values[idx] = chk

                response = ArancinoSpecialChars.CHR_SEP.join(values)

                return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + response + ArancinoSpecialChars.CHR_EOT
            else:
                # return the error code
                return ArancinoCommandErrorCodes.ERR_NULL + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    # region STORE TAGS
    def __OPTS_STORETAGS(self, args):
        '''
        Store tags for a Time Series
        Optional args are:
            - Timestamp (int): UNIX timestamp of the sample. '*' can be used for automatic timestamp (using the system clock)

        MCU → STORE#<key>#<tag1>%<tag2>%<tag3>#<value1>%<value2>%<value3>#<timestamp>@
        MCU → STORE#<key>#<tag1>%<tag2>%<tag3>#<value1>%<value2>%<value3>@

        MCU ← 100@
        '''

        try:
            key = args[0] #"{}:{}".format(args[0], self.__port_id)      # mandatory
            tags = args[1]                                              # mandatory
            values = args[2]                                            # mandatory
            timestamp = None                                            # optional

            if len(args) > 3:
                # the 3th element is the timestamp in unix format. '*' by default
                timestamp = args[3]
            else:
                timestamp = str(int(datetime.now().timestamp() * 1000))

            tags_array = tags.split(ArancinoSpecialChars.CHR_ARR_SEP)
            values_array = values.split(ArancinoSpecialChars.CHR_ARR_SEP)

            if tags_array and values_array and len(tags_array) > 0 and len(values_array) and len(tags_array) == len(values_array):

                for idx, tag in enumerate(tags_array):
                    d_key = "{}:{}:{}:{}".format(self.__port_id, key, SUFFIX_TAG, tag)
                    d_val = values_array[idx]

                    saved_tags = []

                    if self.__datastore_tag.exists(d_key):
                        saved_tags = self.__datastore_tag.lrange(d_key, 0, -1)

                    if not len(saved_tags) or d_val != saved_tags[1]:
                        self.__datastore_tag.lpush(d_key, d_val)
                        self.__datastore_tag.lpush(d_key, timestamp)


            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    # endregion

    #region STORE
    def __OPTS_STORE(self, args):
        '''
        Store the value in a Time Series data structure at key
        Optional args are:
            - Timestamp (int): UNIX timestamp of the sample. '*' can be used for automatic timestamp (using the system clock)

        MCU → STORE#<key>#<values>@
        MCU → STORE#<key>#<values>#<timestamp>@

        MCU ← 100#<timestamp>@
        '''

        try:

            key = "{}:{}".format(self.__port_id, args[0])
            value = float(decimal.Decimal(args[1]))
            timestamp = "*"

            if len(args) > 2:
                # the 3th element is the timestamp in unix format. '*' by default
                timestamp = args[2]

            exist = self.__datastore_tser.redis.exists(key)
            if not exist:
                labels = {
                    #"device_id": self.__conf.get_serial_number(),
                    "port_id": self.__port_id,
                    "port_type": self.__port_type.name
                    }

                if not self.__conf.get_serial_number() == "0000000000000000" and not self.__conf.get_serial_number() == "ERROR000000000":
                    labels["device_id"] = self.__conf.get_serial_number()

                self.__datastore_tser.create(key, labels=labels, duplicate_policy='last', retation=self.__conf.get_redis_timeseries_retation())
                self.__datastore_tser.redis.set("{}:{}".format(key, SUFFIX_TMSTP), 0)  # Starting timestamp 

            ts = self.__datastore_tser.add(key, timestamp, value)

            #self.__datastore_tser
            return ArancinoCommandResponseCodes.RSP_OK + ArancinoSpecialChars.CHR_SEP + str(ts) + ArancinoSpecialChars.CHR_EOT

        except RedisError as ex:
            raise RedisGenericException("Redis Error: " + str(ex), ArancinoCommandErrorCodes.ERR_REDIS)

        except decimal.DecimalException as ex:
            raise ArancinoException("Conversion Error: " + str(ex), ArancinoCommandErrorCodes.ERR_VALUE)

        except Exception as ex:
            raise ArancinoException("Generic Error: " + str(ex), ArancinoCommandErrorCodes.ERR)

    #endregion

    def __get_args_nr_by_cmd_id(self, cmd_id):
        '''
        Get the number of Argument for the specified Command Identifier.

        :param cmd_id: {String} the Command identifier.
        :return: {Integer} the number of arguments for the specified Command Identifier.
        '''

        command = ArancinoCommandIdentifiers.COMMANDS_DICT[cmd_id]
        num = command["args"]

        return num
