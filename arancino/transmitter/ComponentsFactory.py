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
from arancino.transmitter.reader.Reader import Reader
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig,ArancinoConfig2
import importlib

LOG = ArancinoLogger.Instance().getLogger()
#CONF__ = ArancinoConfig.Instance()
CONF = ArancinoConfig2.Instance().cfg
TRACE = CONF.get("log").get("trace")


class ParserFactory:

    """
    Get the Parser instance using the reflection method
    """

    def getParser(self, parserCls, parserCfg) -> Parser:
        class_parser_name = parserCls
        module_parser = importlib.import_module("arancino.transmitter.parser." + class_parser_name)
        class_parser = getattr(module_parser, class_parser_name)
        parser = class_parser(cfg=parserCfg)
        return parser


class SenderFactory:

    """
    Get the Sender instance using the reflection method
    """

    def getSender(self, senderCls, senderCfg) -> Sender:
        class_sender_name = senderCls
        module_sender = importlib.import_module("arancino.transmitter.sender." + class_sender_name)
        class_sender = getattr(module_sender, class_sender_name)
        sender = class_sender(cfg=senderCfg)
        return sender


class ReaderFactory:

    """
    Reader is Singletone: there's only one implementation and instance.
    """

    def getReader(self):
        #Reader is a singleton
        return Reader()