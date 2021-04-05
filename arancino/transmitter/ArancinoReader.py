# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 SmartMe.IO

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
import time
from threading import Thread

from arancino.Arancino import Arancino
from arancino.ArancinoDataStore import ArancinoDataStore
import arancino.ArancinoConstants as CONST
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()


class ArancinoReader(Thread):

    def __init__(self):
        Thread.__init__(self, name='Arancino')
        self.__stop = False
        self.__cycle_time = CONF.get_transmitter_reader_cycle_time()
        self.__log_prefix = ""
        self.__arancino = Arancino()

        # Redis Data Stores
        redis = ArancinoDataStore.Instance()
        self.__datastore_tser = redis.getDataStoreTse()

    def stop(self):
        LOG.info("Stopping Reader...")
        self.__stop = True

    def run(self):
        while not self.__stop:

            try:
                ts_keys = self.__retrieve_ts_keys()

                series = []
                for key in ts_keys:
                    series.append( self.__retrieve_ts_values_by_key(key) )

                # TODO sends data elsewhere
                # parser.receive(series)
                LOG.debug("Time Series Data: " + str(series))

            except Exception as ex:
                LOG.exception("{}Error in the Arancino Reader main loop: {}".format(self.__log_prefix, str(ex)))

            time.sleep(self.__cycle_time)

        LOG.info("Reader Stopped.")



    def __retrieve_ts_values_by_key(self, key):

        timeseries = {}
        try:

            #region # 1. get 'starting' timestamp
            starting_tms_ts = self.__datastore_tser.redis.get("{}:{}".format(key, CONST.SUFFIX_TMSTP))
            values = self.__datastore_tser.range(key, starting_tms_ts, "+")
            #endregion

            #region # 2. get last timestamp and update the starting one
            index = len(values)
            if index > 0:
                ending_tms_ts = int(values[index-1][0]) + 1
                self.__datastore_tser.redis.set("{}:{}".format(key, CONST.SUFFIX_TMSTP), str(ending_tms_ts))
            #endregion

            #region # 3. aggregate timeseries data
            timeseries["key"] = key
            timeseries["values"] = values
            timeseries["labels"] = self.__datastore_tser.info(key).labels
            #endregion

        except Exception as ex:
            LOG.exception("{}Error while getting Time Series values: {}".format(self.__log_prefix, str(ex)))

        finally:
            return timeseries

    def __retrieve_ts_keys(self):

        keys = []
        try:

            #region # 1.  Retrieve all the Keys of Time Series type
            keys_iter = self.__datastore_tser.redis.scan_iter("*")
            for key in keys_iter:
                if self.__datastore_tser.redis.type(key) == "TSDB-TYPE":
                    keys.append(key)
            #endregion

        except Exception as ex:
            LOG.exception("{}Error while getting Time Series keys: {}".format(self.__log_prefix, str(ex)))

        finally:
            return keys
