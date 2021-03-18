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
import redis


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

@Singleton
class ArancinoDataStore:

    def __init__(self):
        conf = ArancinoConfig.Instance()

        redis_instance_type = conf.get_redis_instances_conf()

        self.__redis_dts_std = redis_instance_type[0]   # Standard Data Store
        self.__redis_dts_dev = redis_instance_type[1]   # Device Data Store
        self.__redis_dts_per = redis_instance_type[2]   # Persistent Data Store

        # data store
        self.__redis_pool_dts = redis.ConnectionPool(host=self.__redis_dts_std['host'],
                                                     port=self.__redis_dts_std['port'],
                                                     db=self.__redis_dts_std['db'],
                                                     decode_responses=self.__redis_dts_std['dcd_resp'])

        # device store
        self.__redis_pool_dvs = redis.ConnectionPool(host=self.__redis_dts_dev['host'],
                                                     port=self.__redis_dts_dev['port'],
                                                     db=self.__redis_dts_dev['db'],
                                                     decode_responses=self.__redis_dts_dev['dcd_resp'])

        # data store (reserved keys)
        self.__redis_pool_dts_rsvd = redis.ConnectionPool(host=self.__redis_dts_per['host'],
                                                          port=self.__redis_dts_per['port'],
                                                          db=self.__redis_dts_per['db'],
                                                          decode_responses=self.__redis_dts_per['dcd_resp'])



        self._redis_conn_dts = redis.Redis(connection_pool=self.__redis_pool_dts)
        self._redis_conn_dvs = redis.Redis(connection_pool=self.__redis_pool_dvs)
        self._redis_conn_dts_rsvd = redis.Redis(connection_pool=self.__redis_pool_dts_rsvd)

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

        return self._redis_conn_dts_rsvd


    def closeAll(self):
        try:
            self.getDataStoreStd().connection_pool.disconnect()
            self.getDataStoreDev().connection_pool.disconnect()
            self.getDataStorePer().connection_pool.disconnect()
        except Exception as ex:
            pass
