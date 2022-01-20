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
from arancino.ArancinoCortex import *
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor
import uuid
import time



LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class ArancinoTestPort(ArancinoPort):
    def __init__(self, id=None, device=None, m_s_plugged=True, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, receivedCommandHandler=None, disconnectionHandler=None):
        super().__init__(device=device, port_type=PortTypes.TEST, m_s_plugged=m_s_plugged, m_c_enabled=m_c_enabled, m_c_alias=m_c_alias, m_c_hide=m_c_hide, upload_cmd=CONF.get_port_test_upload_command(), receivedCommandHandler=receivedCommandHandler, disconnectionHandler=disconnectionHandler)

        self._id = id if id is not None else uuid.uuid1()
        self.__stop = False

        self._executor = ArancinoCommandExecutor(port_id=self._id, port_device=self._device, port_type=self._port_type)

        self._compatibility_array = COMPATIBILITY_MATRIX_MOD_TEST[str(CONF.get_metadata_version().truncate())]

        self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)

    # TODO implement the method in the abstract class:
    # NOTA: per farlo astratto, si deve muovere l'handler nella super classe e chiamarlo con un nome generico ed anche il log prefix

    # def __commandReceivedHandler(self, raw_command):
    #     """
    #      This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
    #          It first receives a Raw Command from the Serial Port, then translate it to an ArancinoCommand object
    #          and send it back to another callback function
    #
    #      :param raw_command: the Raw Command received from the Serial port
    #      :return: void.
    #      """
    #     try:
    #         # create an Arancino Comamnd from the raw command
    #         acmd = ArancinoComamnd(raw_command=raw_command)
    #         LOG.debug("{} Received: {}: {}".format(self._log_prefix, acmd.getId(), str(acmd.getArguments())))
    #
    #         # check if the received command handler callback function is defined
    #         if self._received_command_handler is not None:
    #             self._received_command_handler(self._id, acmd)
    #
    #         # call the Command Executor and get a raw response
    #         raw_response = self._executor.exec(acmd)
    #
    #         # create the Arancino Response object
    #         arsp = ArancinoResponse(raw_response=raw_response)
    #
    #         if acmd.getId() == ArancinoCommandIdentifiers.CMD_SYS_START["id"]:
    #             v = semantic_version.Version(acmd.getArguments()[0])
    #             self._setLibVersion(v)
    #
    #     # All Arancino Application Exceptions contains an Error Code
    #     except ArancinoException as ex:
    #
    #         if ex.error_code == ArancinoCommandErrorCodes.ERR_NON_COMPATIBILITY:
    #             self._setComapitibility(False)
    #
    #         arsp = ArancinoResponse(rsp_id=ex.error_code, rsp_args=[])
    #         LOG.error("{} {}".format(self._log_prefix, str(ex)))
    #
    #     # Generic Exception uses a generic Error Code
    #     except Exception as ex:
    #         arsp = ArancinoResponse(rsp_id=ArancinoCommandErrorCodes.ERR, rsp_args=[])
    #         LOG.error("{} {}".format(self._log_prefix, str(ex)))
    #
    #     finally:
    #
    #         try:
    #             # move there that, becouse if there's an non compatibility error, lib version will not setted
    #             #   moving that in the finally, it will setted
    #             if acmd.getId() == ArancinoCommandIdentifiers.CMD_SYS_START["id"]:
    #
    #                 self._retrieveStartCmdArgs(acmd.getArguments())
    #
    #                 # if it is not compatible an error was send back to the mcu and the communnication is not started (the mcu receive an errore and try to connect again)
    #                 # if it is compatible the communication starts and it ready to receive new commands.
    #                 started = True if self.isCompatible() else False
    #                 self._setStarted(started)
    #
    #             # send the response back.
    #             self.sendRespose(arsp.getRaw())
    #             LOG.debug("{} Sending: {}: {}".format(self._log_prefix, arsp.getId(), str(arsp.getArguments())))
    #
    #         except SerialException as ex:
    #             LOG.error("{} Error while transmitting a Response: {}".format(self._log_prefix), str(ex))

    # TODO implement the method in the abstract class:
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

                        if CONF.get_port_test_reset_on_connect():
                            # first resetting
                            self.reset()

                        self.__test_handler = ArancinoTestHandler("ArancinoTestHandler-"+self._id, self._id, self._device, self._commandReceivedHandlerAbs, self.__connectionLostHandler)
                        self.__test_handler.start()
                        self._m_s_connected = True
                        LOG.info("{} Connected".format(self._log_prefix))
                        self._start_thread_time = time.time()


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
        pass
