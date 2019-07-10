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

from arancino import arancino_conf as conf
import redis

class ArancinoDataStore():

    def __init__(self):

        #data store
        self.__redis_pool_dts = redis.ConnectionPool(host=conf.redis_dts['host'], port=conf.redis_dts['port'], db=conf.redis_dts['db'], decode_responses=conf.redis_dts['dcd_resp'])

        #device store
        self.__redis_pool_dvs = redis.ConnectionPool(host=conf.redis_dvs['host'], port=conf.redis_dvs['port'], db=conf.redis_dvs['db'], decode_responses=conf.redis_dvs['dcd_resp'])

        #data store (reserved keys)
        self.__redis_pool_dts_rsvd = redis.ConnectionPool(host=conf.redis_dts_rsvd['host'], port=conf.redis_dts_rsvd['port'], db=conf.redis_dts_rsvd['db'], decode_responses=conf.redis_dts_rsvd['dcd_resp'])

    def getDataStore(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage data received from the microcontrollers.
        :return:
        """

        return redis.Redis(connection_pool=self.__redis_pool_dts)


    def getDeviceStore(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage configurations of Arancino Devices.
        :return:
        """
        return redis.Redis(connection_pool=self.__redis_pool_dvs)

    def getDataStoreRsvd(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage reserved keys, and/or persistent application keys.
        :return:
        """

        return redis.Redis(connection_pool=self.__redis_pool_dts_rsvd)