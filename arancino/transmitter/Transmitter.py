'''
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
'''

from arancino.transmitter.reader.Reader import Reader
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
import importlib

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class Transmitter():

    def __init__(self):

        self.__log_prefix = "Arancino Transmitter - "

        try:

            # region # .1 instance of reader class
            self.__reader = Reader(self.__do_elaboration)
            # endregion

            # region # .2 instance of parser class
            class_parser_name = CONF.get_transmitter_parser_class()
            module_parser = importlib.import_module("arancino.transmitter.parser." + class_parser_name)
            class_parser = getattr(module_parser, class_parser_name)
            self.__parser = class_parser()
            # endregion

            # region # .3 instance of sender class
            class_sender_name = CONF.get_transmitter_sender_class()
            module_sender = importlib.import_module("arancino.transmitter.sender." + class_sender_name)
            class_sender = getattr(module_sender, class_sender_name)
            self.__sender = class_sender()
            # endregion
        except Exception as ex:
            LOG.error("{}Error while starting Trasmitter's componentes : {}".format(self.__log_prefix, str(ex)), exc_info=TRACE)

    def start(self):

        self.__sender.start()
        self.__parser.start()
        self.__reader.start()

    def stop(self):

        self.__sender.stop()
        self.__parser.stop()
        self.__reader.stop()

    def __do_elaboration(self, data):

        parsed_data = self.__parser.parse(data)
        sent = self.__sender.send(parsed_data)

        if sent:
            self.__reader.ack()
        else:
            # TODO do not update timestamp in the time series
            self.__reader.ack()
            pass

