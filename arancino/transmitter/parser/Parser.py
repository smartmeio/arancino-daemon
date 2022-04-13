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
from jinja2 import Template
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig

import os


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class Parser(ABC):

    def __init__(self, cfg=None):
        #private
        self.__cfg = cfg


        #self.__template_file = os.path.join(CONF.get_arancino_template_path(), CONF.get_transmitter_parser_template_file())
        self.__template_file = os.path.join(CONF.get_arancino_template_path(), cfg["parser"]["file"])

        #protected
        self._log_prefix = "Parser [Abstract] - "
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
