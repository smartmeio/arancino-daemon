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
import json
import os

from jinja2 import Template

from arancino.transmitter.parser.Parser import Parser

from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
import jinja2

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()



class ParserTemplate(Parser):

    def __init__(self):
        super()
        self.__log_prefix = "Parser [Json Test] - "
        self.__template_file = os.path.join(CONF.get_arancino_template_path(), CONF.get_transmitter_parser_template_file())
        self.__tmpl = None
        try:
            with open(self.__template_file) as f:
                self.__tmpl = Template(f.read())
        except Exception as ex:
            LOG.error("{}Error while loading template file [{}]: {}".format(self.__log_prefix, self.__template_file, ex), exc_info=TRACE)


    def parse(self, data=None):

        LOG.debug("{}Start Parsing Data...".format(self.__log_prefix))
        data = self.__do_elaboration(data)
        LOG.debug("{}Finish Parsing Data.".format(self.__log_prefix))
        return data

    def __do_elaboration(self, data=None):
        LOG.debug("{}Parsing Data...".format(self.__log_prefix))

        try:

            # do parsing only if data contains data
            if data or len(data) > 0:

                # do parsing only if template is loaded
                if self.__tmpl:
                    output = self.__tmpl.render(data=data)
                    LOG.debug("{}Parsed data: {}".format(self.__log_prefix, output))
                    return output
                else:
                    LOG.warning("{}No template to be parsed.".format(self.__log_prefix))
                    return None

            else:
                LOG.warning("{}No data to parse.".format(self.__log_prefix))
                return None

        except Exception as ex:
            LOG.error("{}Parsing Error: {}".format(self.__log_prefix, ex), exc_info=TRACE)
            return None


