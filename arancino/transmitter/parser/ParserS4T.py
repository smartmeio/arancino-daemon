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

from arancino.transmitter.parser.ParserSimple import ParserSimple
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()



class ParserS4T(ParserSimple):

    def __init__(self, cfg=None):
        super().__init__(cfg=cfg)
        #private
        #self.__db_name = CONF.get_transmitter_parser_s4t_db_name()
        self.__db_name = self.cfg["s4t"]["db_name"]

        #protected
    
    def _do_elaboration(self, data=None):

        rendered_data, metadata = super()._do_elaboration(data)

        if metadata:
            for index, md in enumerate(metadata):
                md["tags"] = data[index]["tags"]
                md["labels"] = data[index]["labels"]
                md["db_name"] = self.__db_name
        
        return rendered_data, metadata


