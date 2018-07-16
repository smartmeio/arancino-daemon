# Copyright 2018 SmartMe.IO
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#   author: sergio tomasello <sergio@smartme.io>
#   date: 2018.07.12
#

__author__ = "Sergio Tomasello <sergio@smartme.io>"

from datetime import datetime
import errno
import json
import os
import psutil
import signal
import subprocess
from urllib.parse import urlparse

from iotronic_lightningrod.modules import Module
from iotronic_lightningrod.modules import utils

import iotronic_lightningrod.wampmessage as WM
import redis
from serial.tools import list_ports

from oslo_config import cfg
from oslo_log import log as logging
LOG = logging.getLogger(__name__)

CONF = cfg.CONF
SERVICES_CONF_FILE = CONF.lightningrod_home + "/services.json"


class SerialManager(Module.Module):

    def __init__(self, board, session):
        super(SerialManager, self).__init__("SerialManager", board)
        #connect to redis
        self.datastore = redis.StrictRedis(host='localhost', port=6379, db=0)
        #keep al plugged serial ports with a specific vid and pid
        self.pluggedports = {} #list(list_ports.grep('2a03:804F'))

    def finalize(self):
        LOG.info("Serial Communication Manager Loading...")

    def restore(self):
        pass

    async def DataStoreGet(self, key):
        self.datastore.get(key)
        #TODO ritornare un messaggio a iotronic - chiedere a nicola

    async def DataStoreSet(self, key, value):
        self.datastore.get(key.value)
        #TODO ritornare un messaggio a iotronic - chiedere a nicola
