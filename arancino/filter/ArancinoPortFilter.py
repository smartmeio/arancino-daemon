# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2020 SmartMe.IO

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

#from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
#from arancino.ArancinoDataStore import ArancinoDataStore
from enum import Enum


class ArancinoPortFilter():

    __metaclass__ = ABCMeta

    def __init__(self):
        pass


    @abstractmethod
    def filterOnly(self, ports={}, list=[]):
        pass


    @abstractmethod
    def filterAll(self, ports={},list=[]):
        pass


    @abstractmethod
    def filterExclude(self, ports={},list=[]):
        pass
    '''
    @abstractmethod
    def checkPubKey(self, public_key):
        __datastore = ArancinoDataStore.Instance()
        chiave = public_key.public_bytes(
            format=PublicFormat.SubjectPublicKeyInfo, encoding=Encoding.PEM)
        chiave = chiave.decode("utf-8")
        whitelist = __datastore.getDataStoreDev().hgetall("WHITELIST")
        verify = False
        for i in whitelist:
            if whitelist[i] == chiave:
                verify = True
        return verify
    '''
class FilterTypes(Enum):
    EXCLUDE = 0
    ONLY = 1
    ALL = 2
    DEFAULT = 2
