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
import json
import uuid
from datetime import datetime


class ArancinoEventMessage:

    def __init__(self):
        self._ID: str = str(uuid.uuid4())
        self._TIMESTAMP: int = int(datetime.now().timestamp() * 1000)
        self._TYPE: str = self.Type.SYSTEM
        self._SOURCE: str = None
        self._MESSAGE = None #[JSON | STRING]
        self._SEVERITY: str = None
        self._AES: str = None
        self._VARS: dict = {}
        self._METADATA: dict = {}


    @property
    def ID(self):
        return self._ID


    @property
    def TIMESTAMP(self):
        return self._TIMESTAMP


    @property
    def TYPE(self):
        return self._TYPE


    @property
    def SOURCE(self):
        return self._SOURCE

    @SOURCE.setter
    def SOURCE(self, source):
        self._SOURCE = source


    @property
    def MESSAGE(self):
        return self._MESSAGE


    @MESSAGE.setter
    def MESSAGE(self, message):
        self._MESSAGE = message


    @property
    def SEVERITY(self):
        return self._SEVERITY


    @SEVERITY.setter
    def SEVERITY(self, severity: str):
        self._SEVERITY = severity


    @property
    def AES(self):
        return self._AES


    @AES.setter
    def AES(self, aes_uuid):
        self._AES = aes_uuid


    @property
    def VARS(self):
        return self._VARS


    @VARS.setter
    def VARS(self, vars: dict):
        self._VARS = vars


    @property
    def METADATA(self):
        return self._METADATA


    @METADATA.setter
    def METADATA(self, metadata: dict):
        self._METADATA = metadata


    def getMessage(self):
        msg = {
            "id": self._ID,
            "timestamp": self._TIMESTAMP,
            "source": self._SOURCE,
            "aes": self._AES,
            "vars": self._VARS,
            "severity": self._SEVERITY,
            "message": self._MESSAGE,
            "metadata": self._METADATA
        }

        return msg


    def getMessageString(self):
        msg_json = self.getMessage()
        msg_str = json.dumps(msg_json)
        return msg_str


    class Type:
        SERVICE = "SERVICE"
        ENDNODE = "ENDNODE"
        SYSTEM = "SYSTEM"

    class Source:
        SERVICE = "SERVICE"
        ENDNODE = "ENDNODE"
        SYSTEM = "SYSTEM"


    class Serverity:
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"