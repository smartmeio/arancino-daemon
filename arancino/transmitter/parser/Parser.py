# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 smartme.IO

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

from abc import ABC, abstractmethod
from enum import Enum
import os
from jinja2 import Template
from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("log").get("trace")
ENV = ArancinoEnvironment.Instance()


class Parser(ABC):

    def __init__(self, cfg=None):
        #private
        self.__cfg = cfg

        # Redis Data Stores
        redis = ArancinoDataStore.Instance()
        self._datastore_tser = redis.getDataStoreTse()
        #self.__template_file = os.path.join(CONF.get_arancino_template_path(), CONF.get_transmitter_parser_template_file())
        self.__template_file = os.path.join(ENV.tmplt_dir, self.cfg.get("file"))


        #protected
        self._flow_name = self.cfg.get("name")
        self._log_prefix = "Flow [{}] - Parser [{}] - ".format(self._flow_name, self.cfg.get("class"))
        self._tmpl = None
        try:
            with open(self.__template_file) as f:
                self._tmpl = Template(f.read())
        except Exception as ex:
            LOG.error("{}Error while loading template file [{}]: {}".format(self._log_prefix, self.__template_file, ex), exc_info=TRACE)


    @property
    def cfg(self):
        return self.__cfg

    def parse(self, data=None):
        LOG.debug("{}Start Parsing Data...".format(self._log_prefix))
        data, metadata = self._do_elaboration(data)
        LOG.debug("{}Finish Parsing Data.".format(self._log_prefix))
        return data, metadata


    @abstractmethod
    def _do_elaboration(self, data=None):
        raise NotImplementedError


    @abstractmethod
    def start(self):
        raise NotImplementedError


    @abstractmethod
    def stop(self):
        raise NotImplementedError


class ParserKind(Enum):
    PARSER_SIMPLE = "ParserSimple"
    PARSER_STACK_4_THINGS = "ParserS4T"
