# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2019 SmartMe.IO

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
import sys
import time

from arancino.utils.ArancinoUtils import Singleton, ArancinoConfig, ArancinoLogger
#import redis
from redistimeseries.client import Client as redis


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

@Singleton
class ArancinoDataStore:

    def __init__(self):

        redis_instance_type = CONF.get_redis_instances_conf()

        self.__redis_dts_std = redis_instance_type[0]   # Standard Data Store
        self.__redis_dts_dev = redis_instance_type[1]   # Device Data Store
        self.__redis_dts_pers = redis_instance_type[2]  # Persistent Data Store
        self.__redis_dts_rsvd = redis_instance_type[3]  # Reserved Data Store
        self.__redis_dts_tse = redis_instance_type[4]   # Time Series Data Store
        self.__redis_dts_tag = redis_instance_type[5]   # Time Series Data Store

        # data store
        self.__redis_pool_dts = redis(host=self.__redis_dts_std['host'],
                                                     port=self.__redis_dts_std['port'],
                                                     db=self.__redis_dts_std['db'],
                                                     decode_responses=self.__redis_dts_std['dcd_resp'])

        # data store (reserved keys)
        self.__redis_pool_dts_rsvd = redis(host=self.__redis_dts_rsvd['host'],
                                                          port=self.__redis_dts_rsvd['port'],
                                                          db=self.__redis_dts_rsvd['db'],
                                                          decode_responses=self.__redis_dts_rsvd['dcd_resp'])


        # device store
        self.__redis_pool_dvs = redis(host=self.__redis_dts_dev['host'],
                                                     port=self.__redis_dts_dev['port'],
                                                     db=self.__redis_dts_dev['db'],
                                                     decode_responses=self.__redis_dts_dev['dcd_resp'])

        # data store persistent
        self.__redis_pool_dts_pers = redis(host=self.__redis_dts_pers['host'],
                                                          port=self.__redis_dts_pers['port'],
                                                          db=self.__redis_dts_pers['db'],
                                                          decode_responses=self.__redis_dts_pers['dcd_resp'])


        # time series
        #self.__redis_pool_tse = redis.ConnectionPool(host=self.__redis_dts_tse['host'],
        self.__redis_pool_tse = redis(host=self.__redis_dts_tse['host'],
                                                     port=self.__redis_dts_tse['port'],
                                                     db=self.__redis_dts_tse['db'],
                                                     decode_responses=self.__redis_dts_tse['dcd_resp'])

        # time series tags
        self.__redis_pool_tag = redis(host=self.__redis_dts_tag['host'],
                                                     port=self.__redis_dts_tag['port'],
                                                     db=self.__redis_dts_tag['db'],
                                                     decode_responses=self.__redis_dts_tag['dcd_resp'])




        self._redis_conn_dts = self.__redis_pool_dts.redis#redis.Redis(connection_pool=self.__redis_pool_dts)
        self._redis_conn_dvs = self.__redis_pool_dvs.redis#redis.Redis(connection_pool=self.__redis_pool_dvs)
        self._redis_conn_dts_rsvd = self.__redis_pool_dts_rsvd.redis#redis.Redis(connection_pool=self.__redis_pool_dts_rsvd)
        self._redis_conn_dts_pers = self.__redis_pool_dts_pers.redis#redis.Redis(connection_pool=self.__redis_pool_dts_pers)
        self._redis_conn_tse = self.__redis_pool_tse#redis.Redis(connection_pool=self.__redis_pool_tse)
        self._redis_conn_tag = self.__redis_pool_tag.redis

        self.__attempts = 1
        self.__attempts_tot = CONF.get_redis_connection_attempts()

        while True:

            try:
                if self.__attempts_tot != -1:
                    LOG.info("Redis Connection attempts: {}".format(str(self.__attempts)))
                else:
                    LOG.info("Redis Connection attempts...")

                self._redis_conn_dts.ping()
                self._redis_conn_dvs.ping()
                self._redis_conn_dts_rsvd.ping()
                self._redis_conn_dts_pers.ping()
                self._redis_conn_tse.redis.ping()
                break

            except Exception as ex:
                if self.__attempts_tot != -1:
                    if self.__attempts == self.__attempts_tot:
                        LOG.error("Cannot connect to Redis: {}".format(str(ex)))
                        sys.exit(-1)

                    self.__attempts += 1
                    time.sleep(3)

        LOG.info("Redis Connection OK")



    def getDataStoreStd(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage data received from the microcontrollers.
        :return:
        """

        return self._redis_conn_dts

    def getDataStoreRsvd(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage data received from the microcontrollers.
        :return:
        """

        return self._redis_conn_dts_rsvd


    def getDataStoreDev(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage configurations of Arancino Devices.
        :return:
        """
        return self._redis_conn_dvs


    def getDataStorePer(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage reserved keys, and/or persistent application keys.
        :return:
        """

        return self._redis_conn_dts_pers

    def getDataStoreTse(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage time series data.
        :return:
        """

        return self._redis_conn_tse

    def getDataStoreTag(self):
        """
        Gets a redis client from a connection pool. This client is used to
            manage yags of time series data.
        :return:
        """

        return self._redis_conn_tag


    def closeAll(self):
        try:
            self.getDataStoreStd().connection_pool.disconnect()
            self.getDataStoreDev().connection_pool.disconnect()
            self.getDataStorePer().connection_pool.disconnect()
            self.getDataStoreRsvd().connection_pool.disconnect()
            self.getDataStoreTse().connection_pool.disconnect()
        except Exception as ex:
            pass
