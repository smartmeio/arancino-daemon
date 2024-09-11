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

from arancino.port.test.ArancinoTestHandler import ArancinoTestHandler
from arancino.port.ArancinoPort import ArancinoPort, PortTypes
#from arancino.ArancinoCortex import *
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment
#from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
import uuid
import time



LOG = ArancinoLogger.Instance().getLogger()

CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("general").get("trace")
ENV = ArancinoEnvironment.Instance()

class ArancinoTestPort(ArancinoPort):
    def __init__(self, id=None, device=None, m_s_plugged=True, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None):
        self._id = id if id is not None else uuid.uuid1()
        super().__init__(id=self._id, device=device, port_type=PortTypes.TEST, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, upload_cmd=CONF.get("port").get("test").get("upload_command"), receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        self.__stop = False
        self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)


    # NOTA: per farlo astratto, si deve muovere l'handler nella super classe e chiamarlo con un nome generico ed anche il log prefix
    def __connectionLostHandler(self):
        self._m_s_connected = False
        #self._m_s_plugged = False

        del self.__test_handler


        LOG.warning("{} Test Port closed.".format(self._log_prefix))

        # check if the disconnection handler callback function is defined
        if self._disconnection_handler is not None:
            self._disconnection_handler(self._id)
        else:  # do nothing
            pass


    # PORT APIs IMPLEMENTATION
    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self._m_c_enabled:
                if not self._m_s_connected:
                    try:

                        LOG.info("{} Connecting...".format(self._log_prefix))

                        if CONF.get("port").get("test").get("reset_on_connect"):
                            # first resetting
                            self.reset()

                        self.__test_handler = ArancinoTestHandler(self._id, self._device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
                        self.__test_handler.start()
                        self._m_s_connected = True
                        LOG.info("{} Connected".format(self._log_prefix))
                        self._start_thread_time = time.time()

                        super().connect()

                    except Exception as ex:
                        # TODO: lasciare il raise????
                        LOG.error("{} Error while connecting: {}".format(self._log_prefix, str(ex)), exc_info=TRACE)
                        raise ex

                else:
                    # TODO LOG or EXCPETION
                    LOG.warning("{} Port already connected".format(self._log_prefix))
                    pass
            else: # not enabled
                #TODO LOG or EXCEPTION
                LOG.warning("{} Port not enabled".format(self._log_prefix))
                pass

        except Exception as ex:
            raise ex

    # TODO implement the method in the abstract class:
    # NOTA: per farlo astratto, si deve muovere l'handler nella super classe e chiamarlo con un nome generico ed anche il log prefix

    def disconnect(self):
        try:

            # check if the device is already
            if self._m_s_connected:
                # self._m_s_connected = False

                self.__test_handler.stop()
                super().disconnect()
                self.stopHeartbeat()


            else:
                LOG.debug("{} Already Disconnected".format(self._log_prefix))

        except Exception as ex:
            raise ex


    def identify(self):
        raise NotImplemented("Identify Function is not available for port {}[{}]".format(self.getId(), self.getPortType().name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)

    def reset(self):
        raise NotImplemented("Reset Function is not available for port {}[{}]".format(self.getId(), self.getPortType().name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)

    def upload(self, firmware):
        raise NotImplemented("Upload Function is not available for port {}[{}]".format(self.getId(), self.getPortType().name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)

    def sendResponse(self, raw_response):
        # Do nothing
        print("raw_response")


    # region MICRO CONTROLLER FAMILY

    def getMicrocontrollerFamily(self):
        return None

    def _setMicrocontrollerFamily(self, microcontroller_family):
        pass

    #endregion