'''
SPDX-license-identifier: Apache-2.0

Copyright (c) 2022 SmartMe.IO

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

from arancino.transmitter.parser import Parser
from arancino.transmitter.sender import Sender
from arancino.transmitter.reader import Reader
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
import importlib

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()


class ParserFactory():

    def getParser(self, parserKind) -> Parser:
        class_parser_name = parserKind
        module_parser = importlib.import_module("arancino.transmitter.parser." + class_parser_name)
        class_parser = getattr(module_parser, class_parser_name)
        return class_parser


class SenderFactory():

    def getSender(self, senderKind) -> Sender:
        class_sender_name = senderKind
        module_sender = importlib.import_module("arancino.transmitter.sender." + class_sender_name)
        class_sender = getattr(module_sender, class_sender_name)
        return class_sender


class ReaderFactory():

    def getReader(self):
        #Reader is a singleton
        return Reader()