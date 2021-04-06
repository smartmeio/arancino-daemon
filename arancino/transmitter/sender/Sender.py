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

from abc import ABCMeta, abstractmethod

class Sender(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        #self.__log_prefix = "Sender [Abstract] - "
        pass

    @abstractmethod
    def send(self, data=None):
        done = self.__do_trasmission(data)
        return done

    @abstractmethod
    def __do_trasmission(self, data=None):
        return True

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
