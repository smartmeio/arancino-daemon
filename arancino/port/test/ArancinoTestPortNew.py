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
from arancino.ArancinoConstants import ArancinoApiResponseCode
from arancino.port.test.ArancinoTestHandler import ArancinoTestHandler
from arancino.port.ArancinoPortNew import ArancinoPort, PortTypes
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
    
    def __init__(self, id=None, device=None, enabled=True, auto_connect=True, alias="", hide=False, receivedCommandHandler=None, disconnectionHandler=None):

        _id = id if id is not None else uuid.uuid1()
        self.__stop = False

        super().__init__(id=_id, device=device, port_type=PortTypes.TEST, enabled=enabled, alias=alias, hide=hide, upload_cmd=None, receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        self._log_prefix = "[{} - ({}) {} at {}]".format(PortTypes(self.type).name, self.alias, self.id, self.device)


    # NOTA: per farlo astratto, si deve muovere l'handler nella super classe e chiamarlo con un nome generico ed anche il log prefix
    def __connectionLostHandler(self):

        if not self.isDisconnected():
            self.disconnect()

        LOG.warning("{} Test Port closed.".format(self._log_prefix))

        # check if the disconnection handler callback function is defined
        if self._disconnection_handler is not None:
            self._disconnection_handler(self.id)
        else:  # do nothing
            pass

    # region STATES and TRANSITIONS CALLBACKS

    def before_plug(self):
        LOG.debug("{} Before Plug: {}...".format(self._log_prefix, self.state.upper()))


    def on_enter_state_plugged(self):
        LOG.debug("{} Entering State: {}...".format(self._log_prefix, self.state.upper()))


    def on_exit_state_plugged(self):
        LOG.debug("{} Exiting State: {}...".format(self._log_prefix, self.state.upper()))


    def after_plug(self):
        LOG.debug("{} After Plug: {}...".format(self._log_prefix, self.state.upper()))


    def before_connect(self):
        try:
            # check if the device is enabledzas

            if self.isEnabled():
            
                try:
                    LOG.info("{} Connecting...".format(self._log_prefix))

                    if CONF.get("port").get("test").get("reset_on_connect"):
                        # first resetting
                        self.reset()

                    self._handler = ArancinoTestHandler(self.id, self.device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
                    self._handler.start()
                    
                    LOG.info("{} Connected".format(self._log_prefix))
                    self._start_thread_time = time.time()

                except Exception as ex:
                    # TODO: lasciare il raise????
                    LOG.error("{} Error while connecting: {}".format(self._log_prefix, str(ex)), exc_info=TRACE)
                    raise ex


            else: # not enabled
                #TODO LOG or EXCEPTION
                LOG.warning("{} Port not enabled".format(self._log_prefix))
                pass

        except Exception as ex:
            raise ex


    def on_enter_state_connected(self):

        LOG.debug("{} Entering State: {}...".format(self._log_prefix, self.state.upper()))


    def on_exit_state_connected(self):
        LOG.debug("{} Exiting State: {}...".format(self._log_prefix, self.state.upper()))


    def after_connect(self):
        LOG.debug("{} After Connect: {}...".format(self._log_prefix, self.state.upper()))


    def before_start(self):
        LOG.debug("{} Before Start: {}...".format(self._log_prefix, self.state.upper()))


    def on_enter_state_started(self):
        LOG.debug("{} Entering State: {}...".format(self._log_prefix, self.state.upper()))


    def on_exit_state_started(self):
        LOG.debug("{} Exiting State: {}...".format(self._log_prefix, self.state.upper()))


    def after_start(self):
        LOG.debug("{} After Start: {}...".format(self._log_prefix, self.state.upper()))


    def before_disconnect(self):
        LOG.debug("{} Before Disconnect: {}...".format(self._log_prefix, self.state.upper()))

        try:

            #TODO PORT MOD verificare se lasciare lo stop()
            self._handler.stop()
            del self._handler
            self.stopHeartbeat()

        except Exception as ex:
            raise ex


    def on_enter_state_disconnected(self):
        LOG.debug("{} Entering State: {}...".format(self._log_prefix, self.state.upper()))


    def on_exit_state_disconnected(self):
        LOG.debug("{} Exiting State: {}...".format(self._log_prefix, self.state.upper()))


    def after_disconnect(self):
        LOG.debug("{} After Disconnect: {}...".format(self._log_prefix, self.state.upper()))
    # endregion

    # PORT APIs IMPLEMENTATION

    def identify(self):
        raise NotImplemented("Identify Function is not available for port {}[{}]".format(self.getId(), self.getPortType().name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)

    def reset(self):
        raise NotImplemented("Reset Function is not available for port {}[{}]".format(self.getId(), self.getPortType().name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)

    def upload(self, firmware):
        raise NotImplemented("Upload Function is not available for port {}[{}]".format(self.getId(), self.getPortType().name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)

    def sendResponse(self, raw_response):
        # Do nothing
        # TODO per fare anche il check del result si dovrebbe spedire il risultato all'handler per verificare se corrisponde al risultato atteso.
        pass
