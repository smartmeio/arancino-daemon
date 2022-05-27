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

from arancino.utils.ArancinoUtils import Singleton, ArancinoConfig, ArancinoConfig2, ArancinoLogger
#import redis
from redistimeseries.client import Client as redis


LOG = ArancinoLogger.Instance().getLogger()
#CONF__ = ArancinoConfig.Instance()
CONF = ArancinoConfig2.Instance().cfg
TRACE = CONF.get("log").get("trace")

@Singleton
class ArancinoDataStore:

    def __init__(self):



        ist_type = CONF.get("redis").get("instance_type").lower()

        db_std = CONF.get("redis").get(ist_type).get("datastore_std_db")# Standard Data Store
        db_dev = CONF.get("redis").get(ist_type).get("datastore_dev_db")# Device Data Store
        db_per = CONF.get("redis").get(ist_type).get("datastore_per_db")# Persistent Data Store
        db_rsvd = CONF.get("redis").get(ist_type).get("datastore_rsvd_db")# Reserved Data Store
        db_tse = CONF.get("redis").get(ist_type).get("datastore_tse_db")# Time Series Data Store
        db_tag = CONF.get("redis").get(ist_type).get("datastore_tag_db")# Time Series Tags Data Store

        host_vol = CONF.get("redis").get(ist_type).get("host_volatile")
        host_per = CONF.get("redis").get(ist_type).get("host_persistent")
        port_vol = CONF.get("redis").get(ist_type).get("port_volatile")
        port_per = CONF.get("redis").get(ist_type).get("port_persistent")

        dcd_rsp = CONF.get("redis").get("decode_response")


        # data store
        self.__redis_pool_dts = redis(host=host_vol, port=port_vol, db=db_std, decode_responses=dcd_rsp)

        # data store (reserved keys)
        self.__redis_pool_dts_rsvd = redis(host=host_vol, port=port_vol, db=db_rsvd, decode_responses=dcd_rsp)

        # device store
        self.__redis_pool_dvs = redis(host=host_per, port=port_per, db=db_dev, decode_responses=dcd_rsp)

        # data store persistent
        self.__redis_pool_dts_pers = redis(host=host_per, port=port_per, db=db_per, decode_responses=dcd_rsp)

        # time series
        self.__redis_pool_tse = redis(host=host_vol, port=port_vol, db=db_tse, decode_responses=dcd_rsp)

        # time series tags
        self.__redis_pool_tag = redis(host=host_per, port=port_per, db=db_tag, decode_responses=dcd_rsp)


        self._redis_conn_dts = self.__redis_pool_dts.redis#redis.Redis(connection_pool=self.__redis_pool_dts)
        self._redis_conn_dvs = self.__redis_pool_dvs.redis#redis.Redis(connection_pool=self.__redis_pool_dvs)
        self._redis_conn_dts_rsvd = self.__redis_pool_dts_rsvd.redis#redis.Redis(connection_pool=self.__redis_pool_dts_rsvd)
        self._redis_conn_dts_pers = self.__redis_pool_dts_pers.redis#redis.Redis(connection_pool=self.__redis_pool_dts_pers)
        self._redis_conn_tse = self.__redis_pool_tse#redis.Redis(connection_pool=self.__redis_pool_tse)
        self._redis_conn_tag = self.__redis_pool_tag.redis

        self.__attempts = 1
        self.__attempts_tot = CONF.get("redis").get("connection_attempts")

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
