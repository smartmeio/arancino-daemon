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
from arancino.transmitter.sender.Sender import Sender
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
import socket

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()



class TcpSocket(Sender):

    def __init__(self):
        super()
        self.__server_host = CONF.get_transmitter_sender_tcp_socket_host()
        self.__server_port = CONF.get_transmitter_sender_tcp_socket_port()
        self.__log_prefix = "Sender [Tcp Socket] - "
        self.__connection = self.__get_connection(self.__server_host, self.__server_port)


    def send(self, data=None):
        return self.__do_trasmission(data)


    def __do_trasmission(self, data=None):
        if self.__connection:
            LOG.debug("{}Sending data to {}:{}...".format(self.__log_prefix, self.__server_host, str(self.__server_port)))
            not_sent = self.__connection.sendall(data.encode())
            if not not_sent:
                LOG.info("{}Data sent to {}:{}".format(self.__log_prefix, self.__server_host, str(self.__server_port)))
                return True
            else:
                LOG.warning("{}Warning  while sending data to {}:{}".format(self.__log_prefix, self.__server_host, str(self.__server_port)))
                return False
        else:
            LOG.warning("{}Can not send data to {}:{}".format(self.__log_prefix, self.__server_host, str(self.__server_port)))
            return False


    def stop(self):
        if self.__connection:
            self.__connection.close()

    def __get_connection(self, ip, port):
        LOG.debug("{}Connecting to {}:{}...".format(self.__log_prefix, self.__server_host, str(self.__server_port)))
        connection = None
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((self.__server_host, self.__server_port))
        except Exception as ex:
            del connection
            connection = None
            LOG.error("{}Error during connecting to {}:{}: {}".format(self.__log_prefix, str(ex), self.__server_host, str(self.__server_port)), exc_info=TRACE)
        finally:
            return connection