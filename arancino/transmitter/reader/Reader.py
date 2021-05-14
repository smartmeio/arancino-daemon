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
TRACE = CONF.get_log_print_stack_trace()


class Reader(Thread):

    def __init__(self, transmitter_handler):
        Thread.__init__(self, name='ArancinoReader')
        self.__stop = False
        self.__cycle_time = CONF.get_transmitter_reader_cycle_time()
        self.__log_prefix = "Arancino Reader - "
        self.__transmitter_handler = transmitter_handler
        self.__arancino = Arancino()
        self.__handy_series = []

        # Redis Data Stores
        redis = ArancinoDataStore.Instance()
        self.__datastore_tser = redis.getDataStoreTse()
        self.__datastore_tag = redis.getDataStoreTag()

    def stop(self):

        LOG.info("Stopping reader...".format(self.__log_prefix))
        self.__stop = True

    def run(self):
        while not self.__stop:

            try:
                # get all the timeseries keys.
                ts_keys = self.__retrieve_ts_keys()
                

                # series = []
                for key in ts_keys:
                    tags = {}
                    starting_tms_ts = int(self.__datastore_tser.redis.get("{}:{}".format(key, CONST.SUFFIX_TMSTP)))
                    tag_keys = self.__retrieve_tags_keys(key)
                    label_keys = self.__retrieve_label_keys(key.split(':')[0])
                    tag_keys += label_keys
                    
                    for tk in tag_keys:
                        k = tk.split(':')[-1]
                        val = self.__datastore_tag.lrange(tk, 0, -1)
                        tags[k] = {}
                        tags[k] = list(zip(list(map(int, val[::2])), val[1::2]))

                    segments = self.find_segments(tags, starting_tms_ts)

                    for segment in segments:
                        values = self.__retrieve_ts_values_by_key(key, *segment)
                        if values:
                            self.__handy_series.append(values)

                LOG.debug("Time Series Data: " + str(self.__handy_series))
                self.__transmitter_handler(self.__handy_series)
                # clear the handy variables
                self.__handy_series = []

            except Exception as ex:
                LOG.exception("{}Error in the main loop: {}".format(self.__log_prefix, str(ex)), exc_info=TRACE)

            time.sleep(self.__cycle_time)

        LOG.info("{}Stopped.".format(self.__log_prefix))

    
    def find_segments(self, tags, ts):
        
        inf_ts = ts
        sup_ts = -1
        segments = []
        min_tags = []

        while sup_ts != '+':
            min_tags = []
            selected_tags = {}

            for k in tags.keys():
                tags[k].sort(key = lambda t: t[0])
                for i in range(0, len(tags[k])):
                    if tags[k][i][0] > inf_ts:
                        min_tags.append((tags[k][i], k))
                        break

            if len(min_tags):
                    min_tags.sort(key = lambda t: t[0][0])
                    sup_ts = min_tags[0][0][0] - 1 

            if inf_ts == sup_ts or len(min_tags) == 0:
                sup_ts = '+'


            for k, item in tags.items():
                for i in range(0, len(item)):
                    if sup_ts == '+':
                        selected_tags[k] = item[-1][1]
                        break
                    elif i == len(item) - 1 and item[i][0] <= inf_ts:
                        selected_tags[k] = item[i][1]
                        break
                    elif item[i][0] <= inf_ts and item[i+1][0] >= sup_ts:
                        selected_tags[k] = item[i][1]
                        break

            segments.append((inf_ts, sup_ts, selected_tags))
            inf_ts = sup_ts + 1 if sup_ts != '+' else sup_ts
        
        return segments


    def ack(self, metadata):

        # when ack is called, the timestamp of the latest read series is updated.
        key = metadata["key"]
        ending_tms_ts = metadata["last_ts"] + 1
        
        self.__datastore_tser.redis.set("{}:{}".format(key, CONST.SUFFIX_TMSTP), str(ending_tms_ts))



        # index = len(self.__handy_values)
        # if index > 0:
        #     ending_tms_ts = int(self.__handy_values[index - 1][0]) + 1
        #     self.__datastore_tser.redis.set("{}:{}".format(key, CONST.SUFFIX_TMSTP), str(ending_tms_ts))

    def __retrieve_ts_values_by_key(self, key, start, end, tags = []):

        timeseries = {}
        try:

            #region # 1. get 'starting' timestamp
            #starting_tms_ts = self.__datastore_tser.redis.get("{}:{}".format(key, CONST.SUFFIX_TMSTP))
            starting_tms_ts = start
            ending_tms_ts = end
            values = self.__datastore_tser.range(key, starting_tms_ts, ending_tms_ts)
            #endregion

            #region # 3. aggregate timeseries data
            index = len(values)
            if index > 0:
                timeseries["key"] = key
                timeseries["timestamps"], timeseries["values"] = map(list, zip(*values))
                timeseries["labels"] = self.__datastore_tser.info(key).labels
                timeseries["tags"] = tags
            #endregion

        except Exception as ex:
            LOG.exception("{}Error while getting Time Series values: {}".format(self.__log_prefix, str(ex)), exc_info=TRACE)

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
            LOG.exception("{}Error while getting Time Series keys: {}".format(self.__log_prefix, str(ex)), exc_info=TRACE)

        finally:
            return keys


    def __retrieve_tags_keys(self, starting_key):

        starting_key = "{}:{}:*".format(starting_key, CONST.SUFFIX_TAG)

        keys = []
        try:

            #region # 1.  Retrieve all the Keys of List type which matches the patttern
            keys_iter = self.__datastore_tag.scan_iter(starting_key)
            for key in keys_iter:
                if self.__datastore_tag.type(key) == "list":
                    keys.append(key)
            #endregion

        except Exception as ex:
            LOG.exception("{}Error while getting Tags Keys keys: {}".format(self.__log_prefix, str(ex)), exc_info=TRACE)

        finally:
            return keys

    def __retrieve_label_keys(self, starting_key):

        starting_key = "{}:{}:*".format(starting_key, CONST.SUFFIX_LBL)

        keys = []
        try:

            #region # 1.  Retrieve all the Keys of List type which matches the patttern
            keys_iter = self.__datastore_tag.scan_iter(starting_key)
            for key in keys_iter:
                if self.__datastore_tag.type(key) == "list":
                    keys.append(key)
            #endregion

        except Exception as ex:
            LOG.exception("{}Error while getting Label Keys keys: {}".format(self.__log_prefix, str(ex)), exc_info=TRACE)

        finally:
            return keys