'''
SPDX-license-identifier: Apache-2.0

Copyright (C) 2019 SmartMe.IO

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

#from arancino.arancino_datastore import ArancinoDataStore
#import arancino.arancino_constants as const

from arancino.ArancinoDataStore import ArancinoDataStore
from arancino.ArancinoConstants import ArancinoDBKeys
from arancino.utils.ArancinoUtils import stringToBool, stringToDatetime, datetimeToString, ArancinoLogger
from arancino.port.ArancinoPort import PortTypes
from datetime import datetime

LOG = ArancinoLogger.Instance().getLogger()


class ArancinoPortSynch:


    def __init__(self):
        self.__devicestore = ArancinoDataStore.Instance().getDataStoreDev()


    def readPortConfig(self, port):

            id = port.getId()
            try:
                is_enabled = stringToBool(self.__devicestore.hget(id, ArancinoDBKeys.C_ENABLED))
                is_hidden = stringToBool(self.__devicestore.hget(id, ArancinoDBKeys.C_HIDE_DEVICE))
                alias = self.__devicestore.hget(id, ArancinoDBKeys.C_ALIAS)
            except Exception as ex:
                LOG.error("Redis Error: {}".format(str(ex)))
                return


            port.setEnabled(is_enabled)
            port.setHide(is_hidden)
            port.setAlias(alias)

            return port


    def writePortConfig(self, port):

        id = port.getId()
        is_enabled = str(port.isEnabled())
        is_hidden = str(port.isHidden())
        alias = port.getAlias()

        try:
            pipeline = self.__devicestore.pipeline()
            pipeline.hset(id, ArancinoDBKeys.C_ENABLED, is_enabled)
            pipeline.hset(id, ArancinoDBKeys.C_HIDE_DEVICE, is_hidden)
            pipeline.hset(id, ArancinoDBKeys.C_ALIAS, alias)
            pipeline.execute()
        except Exception as ex:
            LOG.error("Redis Error: {}".format(str(ex)))


    def writePortBase(self, port):

        id = port.getId()
        port_type = port.getPortType().value
        #creation_date = datetimeToString(port.getCreationDate())
        creation_date = str(datetime.timestamp(port.getCreationDate()))
        #lib_ver = str(port.getLibVersion())
        try:
            pipeline = self.__devicestore.pipeline()
            pipeline.hset(id, ArancinoDBKeys.B_ID, id)
            pipeline.hset(id, ArancinoDBKeys.B_PORT_TYPE, port_type)
            pipeline.hset(id, ArancinoDBKeys.B_CREATION_DATE, creation_date)
            #pipeline.hset(id, ArancinoDBKeys.B_LIB_VER, lib_ver)
            pipeline.execute()
        except Exception as ex:
            LOG.error("Redis Error: {}".format(str(ex)))


    def readPortChanges(self, port):
        id = port.getId()
        try:

            db_val_lud = self.__devicestore.hget(id, ArancinoDBKeys.S_LAST_USAGE_DATE)
            db_val_cd = self.__devicestore.hget(id, ArancinoDBKeys.B_CREATION_DATE)

            if db_val_lud is not None and db_val_lud is not "":
                #db_val_lud = stringToDatetime(db_val_lud)
                db_val_lud = datetime.utcfromtimestamp(float(db_val_lud))
            else:
                db_val_lud = None

            if db_val_cd is not None and db_val_cd is not "":
                #db_val_cd = stringToDatetime(db_val_cd)
                db_val_cd = datetime.utcfromtimestamp(float(db_val_cd))
            else:
                db_val_cd = None

            last_usage_date = db_val_lud# stringToDatetime(self.__devicestore.hget(id, ArancinoDBKeys.S_LAST_USAGE_DATE)) if self.__devicestore.hget(id, ArancinoDBKeys.S_LAST_USAGE_DATE) is not "" and is not None else None
            creation_date = db_val_cd #stringToDatetime(self.__devicestore.hget(id, ArancinoDBKeys.B_CREATION_DATE)) if self.__devicestore.hget(id, ArancinoDBKeys.B_CREATION_DATE) is not "" else None
        except Exception as ex:
            LOG.error("Redis Error: {}".format(str(ex)))
            return


        port.setLastUsageDate(last_usage_date)
        port.setCreationDate(creation_date)

        return port

    def writePortChanges(self, port):
        id = port.getId()
        #last_usage_date = datetimeToString(port.getLastUsageDate()) if port.getLastUsageDate() is not None and not "" else ""
        last_usage_date = str(datetime.timestamp(port.getLastUsageDate())) if port.getLastUsageDate() is not None and not "" else ""
        ###lib_ver = str(port.getLibVersion())
        ###upt_time = str(port.getUptime())
        try:
            pipeline = self.__devicestore.pipeline()
            ###pipeline.hset(id, ArancinoDBKeys.B_LIB_VER, lib_ver)
            pipeline.hset(id, ArancinoDBKeys.S_LAST_USAGE_DATE, last_usage_date)
            ###pipeline.hset(id, ArancinoDBKeys.S_UPTIME, upt_time)
            pipeline.execute()
        except Exception as ex:
            LOG.error("Redis Error: {}".format(str(ex)))



    def portExists(self, port=None, port_id=None):
        try:
            if port:
                return self.__devicestore.exists(port.getId())
            elif port_id:
                return self.__devicestore.exists(port_id)
            else:
                raise Exception("No port specified")
        except Exception as ex:
            LOG.error("Redis Error: {}".format(str(ex)))
