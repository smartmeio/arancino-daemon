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
import json, time, semantic_version, threading
from abc import ABC, abstractmethod
from types import FunctionType, MethodType
from arancino.utils.ArancinoEventMessage import ArancinoEventMessage
from arancino.ArancinoExceptions import ArancinoException, NonCompatibilityException
from arancino.cortex.ExecutorFactory import CortexCommandExecutorFactory
from arancino.cortex.ArancinoPacket import ArancinoCommand, PACKET, ArancinoResponse
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, stringToBool2, ArancinoEnvironment
from arancino.ArancinoConstants import ArancinoCommandErrorCodes, ArancinoReservedChars, CortexCompatibilityLists, ArancinoApiResponseCode
from arancino.ArancinoDataStore import ArancinoDataStore
from datetime import datetime
from enum import Enum
from transitions import Machine, State


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance().cfg
TRACE = CONF.get("general").get("trace")
ERR_CODES = ArancinoCommandErrorCodes
DATASTORE = ArancinoDataStore.Instance()
ENV = ArancinoEnvironment.Instance()

class ArancinoPort(ABC):

    def __init__(self, id=None, device=None, enabled=True, alias="", hide=False, port_type=None, receivedCommandHandler=None, disconnectionHandler=None):


        #region BASE METADATA attributes

        self._id = id                       # è il Serial Number della porta connessa.
        self._device = device               # è una rappresentazione del dispositivo porta ( tty o ip adddress, i.e: "/dev/tty.ACM0")
        self._type = port_type              # tipologia di porta i.e: Serial, Mqtt, etc...
        self._microcontroller_family = None # la famiglia di mcu della porta
        self._generic_attributes = {}       # insieme di attributi generici associati alla porta
        # endregion

        #region BASE STATUS METADATA
        self._last_usage_date = None        # ultima data di utilizzo, ovvero ultimo comando ricevuto
        self._compatible = None             # rappresenta la compatibilità tra la porta ed il demone che la sta gestondo
        self._creation_date = None          # data di creazione della porta
        #endregion

        # region FIRMWARE METADATA
        self._firmware_library_version = None   # versione della libreria arancino in uso sulla porta
        self._firmware_version = None           # versione del firmware in uso sulla porta
        self._firmware_name = None              # nome del firmware in uso sulla porta
        self._firmware_build_datetime = None    # data di compilazione del firmware in uso sulla porta
        self._firmware_core_version = None      # versione del core del firmware  in uso sulla porta
        self._firmware_cortex_version = None    # versione del protocollo cortex implementato dalla libreria
        self._firmware_use_freertos = None      # indica se il firmware usa freertos
        # endregion

        #region OTHER
        self._upload_cmd = upload_cmd           # comando per eseguire upload del firmware sulla porta
        self._reset_on_connect = None
        self._reset_reconnection_delay = None
        #endregion

        #region BASE CONFIGURATION METADATA
        self._enabled = enabled         # indica se la porta è abilita alla connessione/comunicazione
        self._alias = alias             # nome human-readable associato alla porta
        self._hide = hide               # indica se la porta deve essere mostrata in una eventuale rappresentazione su UI
        #endregion

        self._start_thread_time = None      # timestamp di inizio del thread principale, usato per calcolare l'uptime
        self.__first_time = True            # indica se si tratta di un primo caricamento
        self.__HEARTBEAT = None             # oggetto che monitora il funzionamento della porta, attivo solo se in uso freertos
        self._handler = None                # è l'handler dei comandi, ogni sotto classe implementa il suo.
        self._log_prefix = ""

        self.__machine = Machine(model=self,
                                 states=ArancinoPort.states,
                                 transitions=ArancinoPort.transitions,
                                 initial='plugged')

        # region CALLBACK FUNCTIONS
        self._received_command_handler = None
        self._disconnection_handler = None
        self.setReceivedCommandHandler(receivedCommandHandler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        self.setDisconnectionHandler(disconnectionHandler)  # this is the handler to be used whene a disconnection event is triggered
        # endregion

    # region STATE MACHINE DEFINITIONS

    #region STATE & TRANSITIONS
    states = [
        State(name="plugged", on_enter=['on_enter_state_plugged'], on_exit=['on_exit_state_plugged']),
        State(name="connected", on_enter=['on_enter_state_connected'], on_exit=['on_exit_state_connected']),
        State(name="started", on_enter=['on_enter_state_started'], on_exit=['on_exit_state_started']),
        State(name="disconnected", on_enter=['on_enter_state_disconnected'], on_exit=['on_exit_state_disconnected'])
    ]

    transitions = [
        {'trigger': 'plug', 'source': None, 'dest': 'plugged', 'after': 'after_plug', 'before': 'before_plug'},
        {'trigger': 'connect', 'source': 'plugged', 'dest': 'connected', 'after': 'after_connect', 'before': 'before_connect'},
        {'trigger': 'start', 'source': 'connected', 'dest': 'started', 'after': 'after_start', 'before': 'before_start'},
        {'trigger': 'disconnect', 'source': ['plugged', 'connected', 'started'], 'dest': 'disconnected', 'after': 'after_disconnect', 'before': 'before_disconnect'}
    ]
    #endregion

    # region STATE & TRANSITIONS CALLBACKS

    @abstractmethod
    def before_plug(self):
        pass

    @abstractmethod
    def after_plug(self):
        pass

    @abstractmethod
    def on_enter_state_plugged(self):
        pass

    @abstractmethod
    def on_exit_state_plugged(self):
        pass

    @abstractmethod
    def before_connect(self):
        pass

    @abstractmethod
    def after_connect(self):
        pass

    @abstractmethod
    def on_enter_state_connected(self):
        pass

    @abstractmethod
    def on_exit_state_connected(self):
        pass

    @abstractmethod
    def before_start(self):
        pass

    @abstractmethod
    def after_start(self):
        pass

    @abstractmethod
    def on_enter_state_started(self):
        pass

    @abstractmethod
    def on_exit_state_started(self):
        pass

    @abstractmethod
    def before_disconnect(self):
        pass

    @abstractmethod
    def after_disconnect(self):
        pass

    @abstractmethod
    def on_enter_state_disconnected(self):
        pass

    @abstractmethod
    def on_exit_state_disconnected(self):
        pass

    # endregion

    # endregion


    #region ENCAPSULATORS

    #region BASE METADATA Encapsulation

    #region id
    @property
    def id(self):
        return self._id


    def getId(self):
        return self._id

    #endregion

    #region device
    @property
    def device(self):
        return self._device

    def getDevice(self):
        return self._device

    #endregion

    # region type
    @property
    def type(self):
        return self._type

    def getPortType(self):
        return self._type

    # endregion

    # region microcontroller family
    @property
    def microcontroller_family(self):
        return self._microcontroller_family


    def getMicrocontrollerFamily(self):
        return self._microcontroller_family

    #endregion

    # region generic attributes
    @property
    def generic_attributes(self):
        return self._generic_attributes

    """
    @generic_attributes.setter
    def generic_attributes(self, generic_attributes):
        self._generic_attributes = generic_attributes
    """

    def getGenericAttributes(self):
        return self._generic_attributes

    def _setGenericAttributes(self, attributes):
        if attributes:
            self._generic_attributes = attributes
        else:
            self._generic_attributes = {}

    #endregion


    #endregion

    # region BASE STATUS METADATA

    #region creation date
    @property
    def creation_date(self):
        return self._creation_date


    @creation_date.setter
    def creation_date(self, creation_date):
        self._creation_date = creation_date


    def getCreationDate(self):
        return self._creation_date

    def setCreationDate(self, creation_date):
        self.creation_date = creation_date

    #endregion

    #region last usage date
    @property
    def last_usage_date(self):
        return self._last_usage_date


    @last_usage_date.setter
    def last_usage_date(self, last_usage_date):
        self._last_usage_date = last_usage_date


    def getLastUsageDate(self):
        return self._last_usage_date


    def setLastUsageDate(self, last_usage_date):
        self.last_usage_date = last_usage_date

    #endregion

    #region compatible
    @property
    def compatible(self):
        return self._compatible


    @compatible.setter
    def compatible(self, compatible):
        self._compatible = compatible
    #endregion

    #region uptime
    @property
    def uptime(self):
        if self._start_thread_time:
            return time.time() - self._start_thread_time
        else:
            return 0

    def getUptime(self):
        return self.uptime
    #endregion

    #endregion

    #region BASE FIRMWARE METADATA Encapsulation

    #region firmware library version
    @property
    def firmware_library_version(self):
        return self._firmware_library_version

    def getLibVersion(self):
        return self._firmware_library_version

    def getFirmwareLibVersion(self):
        return self._firmware_library_version

    @firmware_library_version.setter
    def firmware_library_version(self, firmware_library_version):
        self._firmware_library_version = firmware_library_version
    #endregion

    #region firmware version
    @property
    def firmware_version(self):
        return self._firmware_version

    @firmware_version.setter
    def firmware_version(self, firmware_version):
        self._firmware_version = firmware_version

    def getFirmwareVersion(self):
        return self._firmware_version

    def _setFirmwareVersion(self, firmware_version):
        self.firmware_version = firmware_version
    #endregion

    #region firmware name
    @property
    def firmware_name(self):
        return self._firmware_name

    def getFirmwareName(self):
        return self._firmware_name

    @firmware_name.setter
    def firmware_name(self, firmware_name):
        self._firmware_name = firmware_name

    def _setFirmwareName(self, firmware_name):
        self.firmware_name = firmware_name

    # endregion firmware name

    #region firmware build datetime
    @property
    def firmware_build_datetime(self):
        return self._firmware_build_datetime

    @firmware_build_datetime.setter
    def firmware_build_datetime(self, firmware_build_datetime):
        self._firmware_build_datetime = firmware_build_datetime

    def getFirmwareBuildDate(self):
        return self._firmware_build_datetime

    def _setFirmwareBuildDate(self, firmware_build_datetime):
        self.firmware_build_datetime = firmware_build_datetime

    # endregion firmware build datetime

    # region firmware core version
    @property
    def firmware_core_version(self):
        return self._firmware_core_version

    @firmware_core_version.setter
    def firmware_core_version(self, firmware_core_version):
        self._firmware_core_version = firmware_core_version

    def getFirmwareCoreVersion(self):
        return self._firmware_core_version

    def _setFirmwareCoreVersion(self, firmware_core_version):
        self.firmware_core_version = firmware_core_version

    # endregion firmware core version

    # region firmware cortex version
    @property
    def firmware_cortex_version(self):
        return self._firmware_cortex_version

    @firmware_cortex_version.setter
    def firmware_cortex_version(self, firmware_cortex_version):
        self._firmware_cortex_version = firmware_cortex_version

    def getFirmwareCortexVersion(self):
        return self._firmware_cortex_version

    def _setFirmwareCortexVersion(self, firmware_cortex_version):
        self.firmware_cortex_version = firmware_cortex_version

    # endregion firmware cortex version

    # region firmware use freertos
    @property
    def firmware_use_freertos(self):
        return self._firmware_use_freertos

    @firmware_use_freertos.setter
    def firmware_use_freertos(self, firmware_use_freertos):
        self._firmware_use_freertos = firmware_use_freertos

    def getFirmwareUseFreeRTOS(self):
        return self._firmware_use_freertos

    def _setFirmwareUseFreeRTOS(self, firmware_use_freertos):
        self.firmware_use_freertos = stringToBool2(firmware_use_freertos)

    # endregion firmware use freertos

    #endregion

    # region OTHER Encapsulation

    # region upload command
    @property
    def upload_cmd(self):
        return self._upload_cmd

    @upload_cmd.setter
    def upload_cmd(self, upload_command):
        self._upload_cmd = upload_command

    def _setUploadCmd(self, upload_cmd):
        if upload_cmd:
            self.__upload_cmd = upload_cmd

    def getUploadCmd(self):
        return self.__upload_cmd

    def getUploadCommand(self):
        return self._upload_cmd

    def _setUploadCommand(self, upload_cmd):
        self._upload_cmd = upload_cmd

    # endregion upload command

    # region reset on connect
    @property
    def reset_on_connect(self):
        return self._reset_on_connect

    # endregion reset on connect

    # endregion



    def isPlugged(self):
        return self.is_plugged()


    def isConnected(self):
        return self.is_connected()


    def isDisconnected(self):
        return self.is_disconnected()



    def isCompatible(self):
        return self.compatible


    def isStarted(self):
        return self.is_started()


    def isEnabled(self):
        return self._enabled


    def setEnabled(self, enabled):
        self._enabled = enabled

    # def getAutoConnect(self):
    #     return self._m_c_auto_connect


    @property
    def alias(self):
        return self._alias


    @alias.setter
    def alias(self, alias):
        self._alias = alias


    def getAlias(self):
        if self._alias is None:
            self._alias = ""

        return self._alias if self._alias else ""


    def setAlias(self, alias):

        if alias is None:
            alias = ""

        self._alias = alias


    def isFirstTimeLoaded(self):
        if(self.__first_time):
            self.__first_time = False
            return True
        else:
            return False


    def isHidden(self):
        return self._hide


    def setHide(self, hide):
        self._hide = hide


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


    #region OPERATIONS

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


    def identify(self):
        """
        Serve ad identificare la porta, ovvero il dispositivo. Utile nel caso
        in si deve trovare un dispositivo tra i molti presenti.
        """
        if self.firmware_use_freertos:
            key_identify = "{}_{}".format(self.id, ArancinoReservedChars.RSVD_KEY_BLINK_ID)
            DATASTORE.getDataStoreRsvd().set(key_identify, "1")
        else:
            raise NotImplemented(
                "Identify Function is not available for port {}[{}] because firmware is running without FreeRTOS".format(
                    self.id, self.type.name), ArancinoApiResponseCode.ERR_NOT_IMPLEMENTED)


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
    #endregion


    #region UTILITIES

    def stopHeartbeat(self):
        try:
            self.__HEARTBEAT.stop()
            del self.__HEARTBEAT
        except AttributeError:
            # If heartbeat does not (yet) exist just exit
            pass

    """
    def _setMicrocontrollerProperties(self):

        # Recupero il tipo di MCU
        mcu = self.microcontroller_family.lower() if self.microcontroller_family else None

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
    """

    @abstractmethod
    def __setMicrocontrollerFamilyProperties(self):
        """
        Questo metodo viene chiamato solo dopo che la MCU FAMILY è stata
        definita. Viene implementato diversamente da ogni Tipo e Famiglia di Porta.
        :return:
        """
        pass


    #endregion


    #region HANDLERS

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
            # LOG.debug("{} Received: {}".format(self._log_prefix, packet))
            acmd = ArancinoCommand(packet=packet)
            # LOG.debug("{} Received: {}: {}".format(self._log_prefix, acmd.id, str(acmd.getUnpackedPacket())))

            # inserisco il port id se non è presente
            if not PACKET.CMD.ARGUMENTS.PORT_ID in acmd.args:
                acmd.args[PACKET.CMD.ARGUMENTS.PORT_ID] = self.id

            # aggiungo il port type
            acmd.args[PACKET.CMD.ARGUMENTS.PORT_TYPE] = self.type.name

            # check if the received command handler callback function is defined
            if self._received_command_handler is not None:
                self._received_command_handler(self.id, acmd)

            # call the Command Executor and get an arancino response
            cxef = CortexCommandExecutorFactory()
            cmd = cxef.getCommandExecutor(cmd=acmd)

            arsp = cmd.execute()

            # pretty print
            formatted_command_json = json.dumps(acmd.getUnpackedPacket(), indent=2)

            LOG.debug("{} Received: {}: {}".format(self._log_prefix, acmd.id, formatted_command_json))

            if acmd.id == "START":  # TODO ArancinoCommandIdentifiers.CMD_SYS_START["id"]:
                self.__retrieveStartCmdArgs(acmd.args)

                # Set FreeRTOS
                if (acmd.args["fw_freertos"] == 1):
                    self._firmware_use_freertos = "1"

                if (self.firmware_use_freertos and self.__HEARTBEAT == None):
                    self.__HEARTBEAT = ArancinoHeartBeat(self, self.sendArancinoEventsMessage)
                    self.__HEARTBEAT.start()

            else:
                if not self.isStarted():
                    #per evitare di non far funzionare le cose, visto che a volte capita che non arrivare uno start ma direttamente il comando,
                    # imposto la porta in modalità di non compatibilità
                    self.compatible = False
        #            else:
        #                if not self.isStarted():
        #                    LOG.warning("{} Received {} but already not Started: Resetting...".format(self._log_prefix, acmd.id))
        #                    self.reset()
        #                    self.disconnect()

        except ArancinoException as ex:
            # if PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT in acmd.cfg and acmd.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] == 1:
            arsp = ArancinoResponse(packet=None)
            arsp.code = ex.error_code

            LOG.error("{} {}".format(self._log_prefix, str(ex)), exc_info=TRACE)

        # Generic Exception uses a generic Error Code
        except Exception as ex:
            # if PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT in acmd.cfg and acmd.cfg[PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] == 1:
            arsp = ArancinoResponse(packet=None)
            arsp.code = ArancinoCommandErrorCodes.ERR

            LOG.error("{} {}".format(self._log_prefix, str(ex)), exc_info=TRACE)

        finally:

            try:
                # pretty print della risposta
                formatted_response_json = json.dumps(arsp.getUnpackedPacket(), indent=2)

                LOG.debug("{} Preparing Response to Send: {}: \n{}".format(self._log_prefix, arsp.code, formatted_response_json))

                if PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT in acmd.cfg and acmd.cfg[
                    PACKET.CMD.CONFIGURATIONS.ACKNOLEDGEMENT] == 1:
                    # send the response back.
                    if self.sendResponse(arsp.getPackedPacket()):
                        LOG.debug("{} Response Sent: {}".format(self._log_prefix, arsp.code))
                else:
                    LOG.debug(
                        "{} Ack disabled, response is not sent back : {}".format(self._log_prefix, arsp.code))
            except Exception as ex:
                LOG.error(
                    "{} Error while transmitting a Response: {}".format(self._log_prefix, str(ex), exc_info=TRACE))


    def __retrieveStartCmdArgs(self, args):

            #region PORT ID
            if args[PACKET.CMD.ARGUMENTS.PORT_ID]:
                old_id = self.id
                self._id = args[PACKET.CMD.ARGUMENTS.PORT_ID]
                DATASTORE.getDataStoreDev().rename(old_id, self.id)
                self._log_prefix = "[{} - ({}) {} at {}]".format(PortTypes(self.type).name, self.alias, self.id, self.device)
                del args[PACKET.CMD.ARGUMENTS.PORT_ID]
            #endregion

            #region LIBRARY VERSION
            arancino_lib_version = None
            arancino_lib_version = args[PACKET.CMD.ARGUMENTS.FIRMWARE.LIBRARY_VERSION]
            arancino_lib_version = semantic_version.Version(arancino_lib_version)
            self._firmware_library_version = arancino_lib_version
            del args[PACKET.CMD.ARGUMENTS.FIRMWARE.LIBRARY_VERSION]
            #endregion

            # region MICRO FAMILY
            arancino_micro_family = None
            arancino_micro_family = args[PACKET.CMD.ARGUMENTS.FIRMWARE.MCU_FAMILY]
            self._microcontroller_family = arancino_micro_family
            del args[PACKET.CMD.ARGUMENTS.FIRMWARE.MCU_FAMILY]
            # endregion

            # region FIRMWARE NAME
            arancino_fw_name = None
            arancino_fw_name = args[PACKET.CMD.ARGUMENTS.FIRMWARE.NAME]
            self._firmware_name = arancino_fw_name
            del args[PACKET.CMD.ARGUMENTS.FIRMWARE.NAME]
            # endregion

            # region FIRMWARE VERSION
            arancino_fw_version = None
            arancino_fw_version = args[PACKET.CMD.ARGUMENTS.FIRMWARE.VERSION]
            arancino_fw_version = semantic_version.Version(arancino_fw_version)
            self._firmware_version = arancino_fw_version
            del args[PACKET.CMD.ARGUMENTS.FIRMWARE.VERSION]
            # endregion

            # region FIRMWARE CORE VERSION
            arancino_fw_core_version = None
            arancino_fw_core_version = args[PACKET.CMD.ARGUMENTS.FIRMWARE.CORE_VERSION]
            arancino_fw_core_version = semantic_version.Version(arancino_fw_core_version)
            self._firmware_core_version = arancino_fw_core_version
            del args[PACKET.CMD.ARGUMENTS.FIRMWARE.CORE_VERSION]
            # endregion

            # region FIRMWARE BUILD DATE TIME
            arancino_firmware_upload_datetime = None
            arancino_firmware_upload_datetime = args[PACKET.CMD.ARGUMENTS.FIRMWARE.BUILD_TIME]
            arancino_firmware_upload_datetime = datetime.strptime(arancino_firmware_upload_datetime,
                                                                  '%b %d %Y %H:%M:%S %z')
            arancino_firmware_upload_datetime = datetime.timestamp(arancino_firmware_upload_datetime)
            arancino_firmware_upload_datetime = datetime.fromtimestamp(arancino_firmware_upload_datetime)
            self._firmware_build_datetime = arancino_firmware_upload_datetime
            del args[PACKET.CMD.ARGUMENTS.FIRMWARE.BUILD_TIME]
            # endregion

            # region FIRMWARE CORTEX VERSION
            arancino_fw_cortex_version = None
            arancino_fw_cortex_version = args[PACKET.CMD.ARGUMENTS.FIRMWARE.CORTEX_VERSION]
            arancino_fw_cortex_version = semantic_version.Version(arancino_fw_cortex_version)
            self._firmware_cortex_version = arancino_fw_cortex_version
            del args[PACKET.CMD.ARGUMENTS.FIRMWARE.CORTEX_VERSION]
            # endregion

            # region GENERIC ATTRIBUTES

            self._setGenericAttributes(args)

            self.__setMicrocontrollerFamilyProperties()

            # endregion

            # region CHECK COMPATIBILITY

            """
            Per semplicità, se la versione del protocollo cortex e la versione in uso nel firmware
            sono nella stessa major version number, allora sono compatibili.
            """

            daemon_cv = ENV.cortex_version
            firmware_cv = self.firmware_cortex_version

            for ls in CortexCompatibilityLists:
                if str(daemon_cv) in ls and str(firmware_cv) in ls:
                    self.compatible = True
                    break

            #started = True if self.compatible else False
            #self._setStarted(started)


            if not self.compatible:
                raise NonCompatibilityException(
                    "Daemon version " + str(CONF.get_metadata_version()) + " can not work with Library version " + str(
                        self.firmware_library_version), ArancinoCommandErrorCodes.ERR_NON_COMPATIBILITY)

            else:
                self.start()

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
        # self.__heartbeat_subscribe()

        self.__heartbeat_subscribe()

        # while not self.__heartbeatStop.is_set():
        while not self.__heartbeatStop:

            time.sleep(self.__heartbeatRate)

            if self.__port.isConnected() and self.__port.isStarted():

                # check sul numero di tentativi
                if self.__heartbeatCount <= self.__heartbeatCountMax:

                    LOG.debug("{} Heartbeat Attempt #{} for the port".format(self._log_prefix,
                                                                             str(self.__heartbeatCount)))

                    # verifico se il primo hb é arrivato
                    if self.__heartbeatTime0:

                        # verifico se il secondo hb é arrivato
                        if self.__heartbeatTime1:

                            ts = self.__heartbeatTime1 - self.__heartbeatTime0

                            if ts <= self.__heartbeatTimeRange:
                                LOG.debug("{} Heartbeat detected: {}".format(self._log_prefix, ts))
                            else:
                                LOG.warn(
                                    "{} Heartbeat detected but over the range: {}".format(self._log_prefix, ts))

                                # crea Arancino Event Message.
                                aem = ArancinoEventMessage()
                                aem.AES = ENV.serial_number
                                aem.MESSAGE = "{} Heartbeat detected but over the range: {}".format(
                                    self._log_prefix, ts)
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
                    # self.stopHeartbeat()

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

    # region heartbeat subscriotion redis
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

    # endregion

class PortTypes(Enum):

    SERIAL = 1  # Serial
    NETWORK = 2  # Wi-Fi or Ethernet Http connection
    TCP = 3  # TCP Socket
    MQTT = 4  # Network MQTT
    BLUETOOTH = 5  # Bluetooth
    TEST = 6  # Fake Port for Test purpose
    UART_BLE = 7  # UART simulated port over BLE
