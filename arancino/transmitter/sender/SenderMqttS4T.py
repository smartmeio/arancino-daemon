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

from arancino.transmitter.sender.SenderMqtt import SenderMqtt
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("log").get("trace")
ENV = ArancinoEnvironment.Instance()

class SenderMqttS4T(SenderMqtt):

    def __init__(self, cfg=None):
        super().__init__(cfg=cfg)
        
    def _do_trasmission(self, data=None, metadata=None):
        tags = ""
        for key, value in metadata["labels"].items():
            tmp = "{}={}".format(key, value)
            tags += tmp + '/'
        for key, value in metadata["tags"].items():
            tmp = "{}={}".format(key, value)
            tags += tmp + '/'
        self._topic = "{}/{}{}".format(metadata["db_name"], tags, metadata["key"].split(':')[1][:-2])
        return super()._do_trasmission(data=data, metadata=metadata)