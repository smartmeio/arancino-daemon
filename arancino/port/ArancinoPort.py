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
import threading
from abc import ABCMeta, abstractmethod
from types import FunctionType, MethodType
from arancino.utils.ArancinoEventMessage import ArancinoEventMessage
import time
import semantic_version
from arancino.ArancinoExceptions import ArancinoException, NonCompatibilityException
from arancino.cortex.ExecutorFactory import CortexCommandExecutorFactory
from arancino.cortex.ArancinoPacket import ArancinoCommand, PACKET, ArancinoResponse
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, stringToBool2, ArancinoEnvironment
from arancino.ArancinoConstants import ArancinoCommandErrorCodes, ArancinoReservedChars, CortexCompatibilityLists, ArancinoApiResponseCode
from arancino.ArancinoDataStore import ArancinoDataStore
import time, semantic_version
from datetime import datetime
from enum import Enum


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("general").get("trace")
ERR_CODES = ArancinoCommandErrorCodes
DATASTORE = ArancinoDataStore.Instance()
ENV = ArancinoEnvironment.Instance()

class ArancinoPort(object):


    __metaclass__ = ABCMeta

    def __init__(self, id=None, device=None, m_s_plugged=False, m_c_enabled=True, m_c_alias="", m_c_hide=False, port_type=None, upload_cmd=None, receivedCommandHandler=None, disconnectionHandler=None):

        #region BASE METADATA
        self._id = id                 # Id is the Serial Number. It will have a value when the Serial Port is connected
        self._device = device           # the plugged tty or ip adddress, i.e: "/dev/tty.ACM0"
        self._port_type = port_type     # Type of port, i.e: Serial, Network, etc...
        self._library_version = None
        self._m_b_creation_date = None
        self._start_thread_time = None
        self._firmware_version = None
        self._firmware_name = None
        self._firmware_build_datetime = None
        self._firmware_core_version = None
        self._firmware_cortex_version = None
        self._firmware_use_freertos = None
        self._microcontroller_family = None
        self._generic_attributes = {}
        #endregion

        #region BASE STATUS METADATA
        self._m_s_plugged = m_s_plugged
        self._m_s_connected = False
        self._m_s_last_usage_date = None
        self._m_s_compatible = None
        self._m_s_started = False
        #endregion

        #region BASE CONFIGURATION METADATA
        self._m_c_enabled = m_c_enabled
        self._m_c_alias = m_c_alias
        self._m_c_hide = m_c_hide
        #credo non serva piu
        ###self._m_c_reset_delay = m_c_reset_delay
        #endregion

        #region OTHER
        self._upload_cmd = upload_cmd
        self._reset_on_connect = None
        self._reset_reconnection_delay = None
        #endregion

        self._log_prefix = ""

        # Command Executor
        # self._executor = ArancinoCommandExecutor(self._id, self._device)

        # Log Prefix to be print in each log
        #self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)

        #region CALLBACK FUNCTIONS
        self._received_command_handler = None
        self._disconnection_handler = None
        self.setReceivedCommandHandler(receivedCommandHandler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        self.setDisconnectionHandler(disconnectionHandler)  # this is the handler to be used whene a disconnection event is triggered
        #endregion

        self.__first_time = True

    def unplug(self):
        self.disconnect()
        self._m_s_plugged = False


    @abstractmethod
    def connect(self):
        """

        :return:
        """
        #####self.startHeartbeat()
        self.__HEARTBEAT = ArancinoHeartBeat(self, self.sendArancinoEventsMessage)
        self.__HEARTBEAT.start()


    @abstractmethod
    def disconnect(self):
        """

        :return:
        """
        #####self.stopHeartbeat()
        self.__HEARTBEAT.stop()
        

    @abstractmethod
    def sendResponse(self, response):
        """
        Send a Response to a "Port". A Response is bind to a Command. The Response is sent only if the
            "Port" is Connected.

        :param response: {String} The Response to send back to the "Port".
        :return: void
        """
        pass


    @abstractmethod
    def reset(self):
        """

        :return:
        """
        pass


    @abstractmethod
    def upload(self, firmware):
        pass


    def _commandReceivedHandlerAbs(self, packet):
        """
        This is an Asynchronous function, and represent the "handler" to be used by an ArancinoHandler implementation to receive data.
            It first receives a Raw Command from the a "Port" (eg. a Serial Port, a Network Port, etc...) , then translate
            it to an ArancinoCommand object and send it back to another callback function

        :param raw_command: the Raw Command received from a "Port"
        :return: void.
        """

        try:
            # create an Arancino Comamnd from the raw command (json or msgpack)
            LOG.debug("{} Received: {}".format(self._log_prefix, packet))
            acmd = ArancinoCommand(packet=packet)
            LOG.debug("{} Received: {}: {}".format(self._log_prefix, acmd.id, str(acmd.getUnpackedPacket())))

            # inserisco il port id se non è presente
            if not PACKET.CMD.ARGUMENTS.PORT_ID in acmd.args:
                acmd.args[PACKET.CMD.ARGUMENTS.PORT_ID] = self.getId()

            #aggiungo il port type
            acmd.args[PACKET.CMD.ARGUMENTS.PORT_TYPE] = self.getPortType().name

            # check if the received command handler callback function is defined
            if self._received_command_handler is not None:
                self._received_command_handler(self._id, acmd)
                
            # call the Command Executor and get an arancino response
            cxef = CortexCommandExecutorFactory()
            cmd = cxef.getCommandExecutor(cmd=acmd)

            arsp = cmd.execute()
            LOG.debug("{} Received: {}: {}".format(self._log_prefix, acmd.id, str(acmd.getUnpackedPacket())))

            if acmd.id == "START": #TODO ArancinoCommandIdentifiers.CMD_SYS_START["id"]:
                self._retrieveStartCmdArgs(acmd.args)

        except ArancinoException as ex:
            #if PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT in acmd.cfg and acmd.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] == 1:
            arsp = ArancinoResponse(packet=None)
            arsp.code = ex.error_code

            LOG.error("{} {}".format(self._log_prefix, str(ex)), exc_info=TRACE)

        # Generic Exception uses a generic Error Code
        except Exception as ex:
            #if PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT in acmd.cfg and acmd.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] == 1:
            arsp = ArancinoResponse(packet=None)
            arsp.code = ArancinoCommandErrorCodes.ERR

            LOG.error("{} {}".format(self._log_prefix, str(ex)), exc_info=TRACE)

        finally:

            try:
                if PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT in acmd.cfg and acmd.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] == 1:
                    # send the response back.
                    self.sendResponse(arsp.getPackedPacket())
                    LOG.debug("{} Sending: {}: {}".format(self._log_prefix, arsp.code, str(arsp.getUnpackedPacket())))
                else:
                    LOG.debug("{} Ack disabled, response is not sent back : {}: {}".format(self._log_prefix, arsp.code, str(arsp.getUnpackedPacket())))

            except Exception as ex:
                LOG.error("{} Error while transmitting a Response: {}".format(self._log_prefix), str(ex), exc_info=TRACE)


    def _retrieveStartCmdArgs(self, args):


        #region port id
        old_id = self._id
        self._id = args[PACKET.CMD.ARGUMENTS.PORT_ID]
        DATASTORE.getDataStoreDev().rename(old_id, self._id)
        self._log_prefix = "[{} - {} at {}]".format(PortTypes(self._port_type).name, self._id, self._device)
        del args[PACKET.CMD.ARGUMENTS.PORT_ID]
        #endregion

        #region library version
        arancino_lib_version = None
        arancino_lib_version = args[PACKET.CMD.ARGUMENTS.FIRMWARE.LIBRARY_VERSION]
        arancino_lib_version = semantic_version.Version(arancino_lib_version)
        self._setLibVersion(arancino_lib_version)
        del args[PACKET.CMD.ARGUMENTS.FIRMWARE.LIBRARY_VERSION]
        #endegion

        # region MICRO FAMILY
        arancino_micro_family = None
        arancino_micro_family = args[PACKET.CMD.ARGUMENTS.FIRMWARE.MCU_FAMILY]
        self._setMicrocontrollerFamily(arancino_micro_family)
        del args[PACKET.CMD.ARGUMENTS.FIRMWARE.MCU_FAMILY]
        # endregion

        # region FIRMWARE NAME
        arancino_fw_name = None
        arancino_fw_name = args[PACKET.CMD.ARGUMENTS.FIRMWARE.NAME]
        self._setFirmwareName(arancino_fw_name)
        del args[PACKET.CMD.ARGUMENTS.FIRMWARE.NAME]
        # endregion

        # region FIRMWARE VERSION
        arancino_fw_version = None
        arancino_fw_version = args[PACKET.CMD.ARGUMENTS.FIRMWARE.VERSION]
        arancino_fw_version = semantic_version.Version(arancino_fw_version)
        self._setFirmwareVersion(arancino_fw_version)
        del args[PACKET.CMD.ARGUMENTS.FIRMWARE.VERSION]
        # endregion

        # region FIRMWARE CORE VERSION
        arancino_fw_core_version = None
        arancino_fw_core_version = args[PACKET.CMD.ARGUMENTS.FIRMWARE.CORE_VERSION]
        arancino_fw_core_version = semantic_version.Version(arancino_fw_core_version)
        self._setFirmwareCoreVersion(arancino_fw_core_version)
        del args[PACKET.CMD.ARGUMENTS.FIRMWARE.CORE_VERSION]
        # endregion

        # region FIRMWARE BUILD DATE TIME
        arancino_firmware_upload_datetime = None
        arancino_firmware_upload_datetime = args[PACKET.CMD.ARGUMENTS.FIRMWARE.BUILD_TIME]
        arancino_firmware_upload_datetime = datetime.strptime(arancino_firmware_upload_datetime, '%b %d %Y %H:%M:%S %z')
        arancino_firmware_upload_datetime = datetime.timestamp(arancino_firmware_upload_datetime)
        arancino_firmware_upload_datetime = datetime.fromtimestamp(arancino_firmware_upload_datetime)
        self._setFirmwareBuildDate(arancino_firmware_upload_datetime)
        del args[PACKET.CMD.ARGUMENTS.FIRMWARE.BUILD_TIME]
        # endregion

        # region FIRMWARE CORTEX VERSION
        arancino_fw_cortex_version = None
        arancino_fw_cortex_version = args[PACKET.CMD.ARGUMENTS.FIRMWARE.CORTEX_VERSION]
        arancino_fw_cortex_version = semantic_version.Version(arancino_fw_cortex_version)
        self._setFirmwareCortexVersion(arancino_fw_cortex_version)
        del args[PACKET.CMD.ARGUMENTS.FIRMWARE.CORTEX_VERSION]
        # endregion

        # region GENERIC ATTRIBUTES

        self._setGenericAttributes(args)

        # endregion

        # region CHECK COMPATIBILITY

        """
        Per semplicità, se la versione del protocollo cortex e la versione in uso nel firmware
        sono nella stessa major version number, allora sono compatibili.
        """

        daemon_cv = CONF.get_metadata_cortex_version()
        firmware_cv = self.getFirmwareCortexVersion()

        for ls in CortexCompatibilityLists:
            if str(daemon_cv) in ls and str(firmware_cv) in ls:
                self._setComapitibility(True)
                break

        started = True if self.isCompatible() else False

        self._setStarted(started)

        if not self.isCompatible():
            raise NonCompatibilityException(
                "Daemon version " + str(CONF.get_metadata_version()) + " can not work with Library version " + str(
                    self.getLibVersion()), ArancinoCommandErrorCodes.ERR_NON_COMPATIBILITY)


    @abstractmethod
    def __connectionLostHandler(self):
        """
        This is an Asynchronous function, and represent the "handler" to be used by an ArancinoHandler implementation to trigger a disconnection event.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """
        pass

    @abstractmethod
    def sendArancinoEventsMessage(self, message: ArancinoEventMessage):
        try:

            ds = DATASTORE.getDataStoreStd()
            channel = "events"
            message = message.getMessageString()
            num = ds.publish(channel, message)

            if num == 0:
                LOG.warn("{} No clients received Arancino Event Message. Is Arancino Interface running?".format(self._log_prefix))

        except Exception as ex:
            LOG.error("{} Error while sending Arancino Event Message: {}".format(self._log_prefix, str(ex)), exc_info=TRACE)


    def identify(self):
        if self.getFirmwareUseFreeRTOS():
            key_identify = "{}_{}".format(self.getId(), ArancinoReservedChars.RSVD_KEY_BLINK_ID)
            DATASTORE.getDataStoreRsvd().set(key_identify, "1")
        else:
            raise NotImplemented("Identify Function is not available for port {}[{}] because firmware is running without FreeRTOS".format(self.getId(), self.getPortType().name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)
        


    # region ID
    def getId(self):
        return self._id

    def _setId(self, id):
        self._id(id)

    #endregion

    # region DEVICE
    def getDevice(self):
        return self._device


    def _setDevice(self, device):
        self._device = device

    # endregion

    # region PORT TYPE
    def getPortType(self):
        return self._port_type


    def _setPortType(self, port_type):
        self._port_type = port_type

    # endregion

    # region LIBRARY VERSION
    def getLibVersion(self):
        return self._library_version


    def _setLibVersion(self, library_version):
        self._library_version = library_version

    # endregion

    # region PORT CREATION DATE
    def getCreationDate(self):
        return self._m_b_creation_date


    def setCreationDate(self, creation_date):
        self._m_b_creation_date = creation_date

    # endregion

    # region LAST USAGE DATE
    def getLastUsageDate(self):
        return self._m_s_last_usage_date


    def setLastUsageDate(self, last_usage_date):
        self._m_s_last_usage_date = last_usage_date

    # endregion

    # region UPTIME
    def getUptime(self):
        if self._start_thread_time:
            return time.time() - self._start_thread_time
        else:
            return 0

    # endregion

    # region FIRMWARE VERSION
    def getFirmwareVersion(self):
        return self._firmware_version


    def _setFirmwareVersion(self, firmware_version):
        self._firmware_version = firmware_version

    # endregion

    # region FIRMWARE NAME
    def getFirmwareName(self):
        return self._firmware_name


    def _setFirmwareName(self, firmware_name):
        self._firmware_name = firmware_name

    # endregion

    # region FIRMWARE BUILD DATE
    def getFirmwareBuildDate(self):
        return self._firmware_build_datetime

    def _setFirmwareBuildDate(self, firmware_build_datetime):
        self._firmware_build_datetime = firmware_build_datetime

    # endregion

    # region CORE VERSION
    def getFirmwareCoreVersion(self):
        return self._firmware_core_version

    def _setFirmwareCoreVersion(self, firmware_core_version):
        self._firmware_core_version = firmware_core_version

    # endregion

    # region MICRO CONTROLLER FAMILY

    def getMicrocontrollerFamily(self):
        return self._microcontroller_family

    def _setMicrocontrollerFamily(self, microcontroller_family):
        self._microcontroller_family = microcontroller_family
        # initially it's setted to the default value for a generic serial port. when mcu family is retrieved then update the value
        #  for the specific mcu family
        #self._reset_delay = getattr(CONF, "get_port_serial_{}_reset_reconnection_delay()".format(microcontroller_family.lower()))

    def _setPortProperties(self):

        if self.getPortType() == PortTypes.SERIAL:

            # Recupero le proprietà di base della porta seriale
            self.setResetReconnectionDelay(CONF.get("port").get("serial").get("reset_reconnection_delay"))
            self._setUploadCommand(CONF.get("port").get("serial").get("upload_command"))

        else:

            # Altrimenti imposto quelle generiche
            self.setResetReconnectionDelay(CONF.get("port").get("reset_reconnection_delay"))
            self._setUploadCommand(CONF.get("port").get("upload_command"))


    def _setMicrocontrollerProperties(self):

        # Recupero il tipo di MCU
        mcu = self.getMicrocontrollerFamily().lower() if self.getMicrocontrollerFamily() else None

        if mcu:

            if self.getPortType() == PortTypes.SERIAL:
                #Quando la port è SERIAL e l'MCU è definito

                if mcu in CONF.get("port").get("serial").get("mcu_type_list"):

                    # Se
                    self.setResetReconnectionDelay(CONF.get("port").get("serial").get(mcu).get("reset_reconnection_delay"))
                    self._setUploadCommand(CONF.get("port").get("serial").get(mcu).get("upload_command"))
                else:
                    self.setResetReconnectionDelay(CONF.get("port").get("serial").get("reset_reconnection_delay"))
                    self._setUploadCommand(CONF.get("port").get("serial").get("upload_command"))

            else:
                self.setResetReconnectionDelay(CONF.get("port").get("reset_reconnection_delay"))
                self._setUploadCommand(CONF.get("port").get("upload_command"))
        else:
            self.setResetReconnectionDelay(CONF.get("port").get("reset_reconnection_delay"))
            self._setUploadCommand(CONF.get("port").get("upload_command"))

    #endregion

    # region FIRMWARE USE FREE RTOS
    def getFirmwareUseFreeRTOS(self):
        return self._firmware_use_freertos

    def _setFirmwareUseFreeRTOS(self, firmware_use_freertos):

        self._firmware_use_freertos = stringToBool2(firmware_use_freertos)
    # endregion

    # region FIRMWARE CORTEX VERSION
    def getFirmwareCortexVersion(self):
        return self._firmware_cortex_version

    def _setFirmwareCortexVersion(self, firmware_cortex_version):
        self._firmware_cortex_version = firmware_cortex_version

    # endregion

    def getUploadCommand(self):
        return self._upload_cmd

    def _setUploadCommand(self, upload_cmd):
        self._upload_cmd = upload_cmd


    #region BASE STATUS METADATA Encapsulators

    def isPlugged(self):
        return self._m_s_plugged


    def isConnected(self):
        return self._m_s_connected


    def isCompatible(self):
        return self._m_s_compatible


    def _setComapitibility(self, comp):
        self._m_s_compatible = comp


    def _setStarted(self, started):
        self._m_s_started = started

    def isStarted(self):
        return self._m_s_started

    #endregion

    #region BASE CONFIGURATION METADATA Encapsulators

    def isEnabled(self):
        return self._m_c_enabled


    def setEnabled(self, enabled):
        self._m_c_enabled = enabled

    # def getAutoConnect(self):
    #     return self._m_c_auto_connect

    def getAlias(self):
        if self._m_c_alias is None:
            self._m_c_alias = ""

        return self._m_c_alias if self._m_c_alias else ""


    def setAlias(self, alias):

        if alias is None:
            alias = ""

        self._m_c_alias = alias



    def isHidden(self):
        return self._m_c_hide


    def setHide(self, hide):
        self._m_c_hide = hide


    def isFirstTimeLoaded(self):
        if(self.__first_time):
            self.__first_time = False
            return True
        else:
            return False

    #endregion

    #region GENERIC ATTRIBUTES

    def getGenericAttributes(self):
        return self._generic_attributes

    def _setGenericAttributes(self, attributes):
        if attributes:
            self._generic_attributes = attributes
        else:
            self._generic_attributes = {}

    #endregion

    #region UPLOAD CMD
    def _setUploadCmd(self, upload_cmd):
        if upload_cmd:
            self.__upload_cmd = upload_cmd

    def getUploadCmd(self):
        return self.__upload_cmd
    #endregion

    #region Set Handlers

    def setDisconnectionHandler(self, disconnection_handler):
        if isinstance(disconnection_handler, FunctionType) or isinstance(disconnection_handler, MethodType):
            self._disconnection_handler = disconnection_handler
        else:
            self._disconnection_handler = None


    def setReceivedCommandHandler(self, received_command_handler):
        if isinstance(received_command_handler, FunctionType) or isinstance(received_command_handler, MethodType):
            self._received_command_handler = received_command_handler
        else:
            self._received_command_handler = None

    #endregion


class ArancinoHeartBeat(threading.Thread):

    def __init__(self, port, sendEventHandler):
        
        self.__port = port
        self.__name = "{}-{}".format(self.__class__.__name__, self.__port.getId())
        self.__sendEventHandler = sendEventHandler
        threading.Thread.__init__(self, name=self.__name)

        port_type = port._port_type.name.lower() 
        
        # heartbeat configuration
        self.__heartbeatRate = CONF.get("port").get(port_type).get("heartbeat_rate")
        self.__heartbeatTimeRange = CONF.get("port").get(port_type).get("heartbeat_time")
        self.__heartbeatCountMax = CONF.get("port").get(port_type).get("heartbeat_attempts")    
        
        # heartbeat control variables
        self.__heartbeatCount = 1
        self.__heartbeatStop = True
        self.__heartbeatTime0 = None
        self.__heartbeatTime1 = None

        self.__redis_heartbeat_pubsub = DATASTORE.getDataStoreRsvd().pubsub()
        self.__redis_heartbeat_pubsub_thread = None
        self.__redis_hearbeat_ch0 = "{}_HB0".format(self.__port.getId())
        self.__redis_hearbeat_ch1 = "{}_HB1".format(self.__port.getId())
        
        self._log_prefix = "Heartbeat [{} - {}]".format(str(port._port_type.name), port.getId())

    def stop(self):
        self.__redis_heartbeat_pubsub.unsubscribe(self.__redis_hearbeat_ch0)
        self.__redis_heartbeat_pubsub.unsubscribe(self.__redis_hearbeat_ch0)
        if self.__redis_heartbeat_pubsub_thread:
            self.__redis_heartbeat_pubsub_thread.stop()

        self.__heartbeatStop = True




    def run(self):
        LOG.info("{} Start Heartbeat".format(self._log_prefix))
        self.__heartbeatStop = False
        #self.__heartbeat_subscribe()

        self.__heartbeat_subscribe()

        #while not self.__heartbeatStop.is_set():
        while not self.__heartbeatStop:

            time.sleep(self.__heartbeatRate)

            if self.__port.isConnected() and self.__port.isStarted():

                # check sul numero di tentativi
                if self.__heartbeatCount <= self.__heartbeatCountMax:
                    
                    LOG.debug("{} Heartbeat Attempt #{} for the port".format(self._log_prefix, str(self.__heartbeatCount)))

                    # verifico se il primo hb é arrivato
                    if self.__heartbeatTime0:
                        
                        # verifico se il secondo hb é arrivato 
                        if self.__heartbeatTime1:
                            
                            ts = self.__heartbeatTime1 - self.__heartbeatTime0

                            if ts <= self.__heartbeatTimeRange:
                                LOG.debug("{} Heartbeat detected: {}".format(self._log_prefix, ts))
                            else:
                                LOG.warn("{} Heartbeat detected but over the range: {}".format(self._log_prefix, ts))

                                # crea Arancino Event Message.
                                aem = ArancinoEventMessage()
                                aem.AES = ENV.serial_number
                                aem.MESSAGE = "{} Heartbeat detected but over the range: {}".format(self._log_prefix, ts)
                                aem.SEVERITY = aem.Serverity.WARNING
                                aem.SOURCE = "DAEMON"

                                # invia Arancino Event Message tramite Handler esterno.
                                self.__sendEventHandler(aem)


                            # reset delle variabili
                            self.__heartbeatTime0 = None
                            self.__heartbeatTime1 = None
                            self.__heartbeatCount = 1

                        # se non é arrivato il secondo hb incremento il contatore
                        else:
                            self.__heartbeatCount += 1
                            
                    
                    # se non é arrivato il primohb incremento il contatore
                    else:
                        self.__heartbeatCount += 1
                    
                else:
                    LOG.warn("{} No Heartbeat detected for the port.".format(self._log_prefix))
                     #self.stopHeartbeat()

                    # Create Arancino Event Message.
                    aem = ArancinoEventMessage()
                    aem.AES = ENV.serial_number
                    aem.MESSAGE = "{} No Heartbeat detected for the port.".format(self._log_prefix)
                    aem.SEVERITY = aem.Serverity.ERROR
                    aem.SOURCE = "DAEMON"

                    # invia Arancino Event Message tramite Handler esterno.
                    self.__sendEventHandler(aem)


                    self.__port.disconnect()

        LOG.info("{} End Heartbeat".format(self._log_prefix))

    #region heartbeat subscriotion redis
    def __heartbeat_subscribe(self):

        self.__redis_heartbeat_pubsub.subscribe(**{
            self.__redis_hearbeat_ch0: self.__heartbeat_sub_0,
            self.__redis_hearbeat_ch1: self.__heartbeat_sub_1
        })
        self.__redis_heartbeat_pubsub_thread = self.__redis_heartbeat_pubsub.run_in_thread(sleep_time=.01)


    def __heartbeat_sub_0(self, data):
        LOG.debug("RECEIVING HB 0: {}".format(data))
        ts_str = data['data']
        self.__heartbeatTime0 = int(datetime.now().timestamp() * 1000)

    def __heartbeat_sub_1(self, data):
        LOG.debug("RECEIVING HB 1: {}".format(data))
        ts_str = data['data']
        self.__heartbeatTime1 = int(datetime.now().timestamp() * 1000)

    def __heartbeat_convert_timestamp(self, ts_str):

        ts = None
        try:
            ts = float(ts_str)
        except ValueError as ex:
            LOG.error("{} Conversion Error: {}".format(self._log_prefix, str(ex)), exc_info=TRACE)
        finally:
            return ts

    #endregion


class PortTypes(Enum):

    SERIAL = 1        # Serial
    NETWORK = 2       # Wi-Fi or Ethernet Http connection
    TCP = 3           # TCP Socket
    MQTT = 4          # Network MQTT
    BLUETOOTH = 5     # Bluetooth
    TEST = 6          # Fake Port for Test purpose
    UART_BLE = 7      # UART simulated port over BLE
