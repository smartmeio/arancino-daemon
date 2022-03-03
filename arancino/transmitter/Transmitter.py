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

from abc import ABC, abstractmethod
from enum import Enum

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()


from Flows import *
from typing import List

class Transmitter():

    def __init__(self):

        self.__log_prefix = "Arancino Transmitter - "
        self.__flows: List[Flow] = []


        try:
            if CONF.is_transmitter_enabled():
                # region # .1 create the transmitter flows

                """
                f1: FlowTemplate = FlowSmartme()
                f2: FlowTemplate = FlowClient()

                f1.load_configuration()
                f2.load_configuration()
                """

                flow_list_name = CONF.get_transmitter_flows()
                for f in flow_list_name:
                    flow: Flow = Flow(f)
                    self.__flows.append(flow)




                # endregion

            else:
                LOG.warning("{} Can Not Start: Disabled".format(self.__log_prefix))

        except Exception as ex:
            LOG.error("{}Error while starting Transmitter's components : {}".format(self.__log_prefix, str(ex)),
                      exc_info=TRACE)


    def start(self):
        if CONF.is_transmitter_enabled():
            for flow in self.__flows:
                flow.start()

    def stop(self):
        if CONF.is_transmitter_enabled():
            for flow in self.__flows:
                flow.stop()


    """
    def __init__(self):

        self.__log_prefix = "Arancino Transmitter - "

        try:
            if CONF.is_transmitter_enabled():
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
            else:
                LOG.warning("{} Can Not Start: Disabled".format(self.__log_prefix))

        except Exception as ex:
            LOG.error("{}Error while starting Transmitter's components : {}".format(self.__log_prefix, str(ex)), exc_info=TRACE)

    def start(self):
        if CONF.is_transmitter_enabled():
            self.__sender.start()
            self.__parser.start()
            self.__reader.start()

    def stop(self):
        if CONF.is_transmitter_enabled():
            self.__sender.stop()
            self.__parser.stop()
            self.__reader.stop()

    def __do_elaboration(self, data):

        parsed_data, parsed_metadata = self.__parser.parse(data)

        # send data only if parsing is ok.
        if parsed_data:

            for index, segment_to_send in enumerate(parsed_data):
                sent = self.__sender.send(segment_to_send, parsed_metadata[index])

                # if parsing
                if sent:
                    # DO update the time series calling "ack" of the Reader
                    self.__reader.ack(parsed_metadata[index])
                else:
                    # DO NOT update timestamp in the time series
                    return

        else:
            # DO NOT update timestamp in the time series
            pass
    """