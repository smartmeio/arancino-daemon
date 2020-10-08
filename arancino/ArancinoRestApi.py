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
import subprocess
import time
import netifaces
import os
from arancino.Arancino import Arancino
from arancino.utils.ArancinoUtils import ArancinoConfig, secondsToHumanString, ArancinoLogger
from arancino.ArancinoConstants import ArancinoApiResponseCode
from arancino.ArancinoPortSynchronizer import ArancinoPortSynch
from arancino.ArancinoConstants import ArancinoDBKeys
from uptime import uptime
from socket import gethostname, gethostbyname
from platform import system, release

from arancino.port.ArancinoPort import PortTypes

API_CODE = ArancinoApiResponseCode()
DB_KEYS = ArancinoDBKeys()
CONF = ArancinoConfig.Instance()
LOG = ArancinoLogger.Instance().getLogger()

class ArancinoApi():

    def __init__(self):

        self.__arancino = Arancino()
        #self.__conf = ArancinoConfig.Instance()
        self.__synchronizer = ArancinoPortSynch()


    #### QUERIES ####
    def hello(self):
        try:
            sys_upt = uptime()
            ara_upt = self.__arancino.getUptime()

            c = self.__getListOfPortConnected()
            d = self.__getListOfPortDiscovered()

            response = {
                "arancino": {
                    "system": {
                        "os": self.__getOsInfo(),
                        "network": {
                            "hostname": gethostname(),
                            "ifaces": self.__getNetwork(), #[gethostname(), gethostbyname(gethostname())],
                        },
                        "uptime": [sys_upt, secondsToHumanString(int(sys_upt))]
                    },
                    "arancino": {
                        "uptime" : [ara_upt, secondsToHumanString(int(ara_upt))],
                        "version": str(CONF.get_metadata_version()),
                        "ports": {
                            "discovered": d,
                            "connected": c
                        },
                        "env": {
                            "ARANCINO": os.environ.get('ARANCINO'),
                            "ARANCINOCONF": os.environ.get('ARANCINOCONF'),
                            "ARANCINOLOG": os.environ.get('ARANCINOLOG'),
                            "ARANCINOENV": os.environ.get('ARANCINOENV')
                        }
                    }
                }
            }

            return response, 200
        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def arancino(self):
        try:
            ara_upt = self.__arancino.getUptime()

            c = self.__getListOfPortConnected()
            d = self.__getListOfPortDiscovered()

            response = {
                "arancino": {
                    "arancino": {
                        "uptime": [ara_upt, secondsToHumanString(int(ara_upt))],
                        "version": str(CONF.get_metadata_version()),
                        "ports": {
                            "discovered": d,
                            "connected": c
                        },
                        "env":{
                            "ARANCINO": os.environ.get('ARANCINO'),
                            "ARANCINOCONF": os.environ.get('ARANCINOCONF'),
                            "ARANCINOLOG": os.environ.get('ARANCINOLOG'),
                            "ARANCINOENV": os.environ.get('ARANCINOENV')
                        }
                    }
                }
            }
            return response, 200

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def system(self):

        try:
            sys_upt = uptime()

            response = {
                "arancino": {
                    "system": {
                        "os": self.__getOsInfo(),
                        "network": {
                            "hostname": gethostname(),
                            "ifaces": self.__getNetwork(),  # [gethostname(), gethostbyname(gethostname())],
                        },
                        "uptime": [sys_upt, secondsToHumanString(int(sys_upt))]
                    }
                }
            }

            return response, 200
        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def getAllPorts(self):
        try:
            ports_conn = []
            for id, port in self.__arancino.getConnectedPorts().items():
                rp = self.__apiCreatePortResponse(port)
                ports_conn.append(rp)

            ports_disc = []
            for id, port in self.__arancino.getDiscoveredPorts().items():
                rp = self.__apiCreatePortResponse(port)
                ports_disc.append(rp)

            response = {
                "arancino" : {
                    "arancino" : {
                        "ports" : {
                            "connected": ports_conn,
                            "discovered": ports_disc
                        }
                    }
                }
            }

            return response, 200

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def getPort(self, port_id=None):

        try:
            response = {}
            port = self.__arancino.findPort(port_id)
            if port is not None:
                response = {
                    "arancino": {
                        "arancino": {
                            "port": self.__apiCreatePortResponse(port)
                        }
                    }
                }

            return response, 200

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def getPortsConnected(self):
        try:
            ports = []
            for id, port in self.__arancino.getConnectedPorts().items():
                rp = self.__apiCreatePortResponse(port)
                ports.append(rp)

            response = {
                "arancino" : {
                    "arancino" : {
                        "ports" : {
                            "connected": ports
                        }
                    }
                }
            }

            return response, 200

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def getPortsDiscovered(self):
        try:
            ports = []
            for id, port in self.__arancino.getDiscoveredPorts().items():
                rp = self.__apiCreatePortResponse(port)
                ports.append(rp)

            response = {
                "arancino" : {
                    "arancino" : {
                        "ports" : {
                            "discovered": ports
                        }
                    }
                }
            }

            return response, 200

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def __getArancinoConf(self):
        # return all the configurations
        try:
            config = CONF.get_config_all()
            response = {
                "arancino": {
                    "config": config
                }
            }
            return response, 200

        except Exception as ex:
            raise ex

    def getArancinoConf(self, params=None):
        try:
            if(params and params["config"]): # check if there's the "config" key in the json, else return all the configuration.

                config = {}

                for it in params["config"]:
                    section = it["section"]
                    option = it["option"]

                    if section not in config:
                        config[section] = {}

                    #if option not in config[section]:
                    config[section][option] = CONF.get_config_by_name(section, option)

                    print(config)

                response = {
                    "arancino": {
                        "config": config
                    }
                }
                return response, 200

            else:
                return self.getArancinoConf(), 200

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500
    #
    # def getArancinoConf(self, section, option):
    #     pass


    #### OPERATIONS ####
    def resetPort(self, port_id):
        try:
            port = self.__arancino.findPort(port_id)

            if port:

                self.__arancino.pauseArancinoThread()
                while not self.__arancino.isPaused():
                    pass
                result = port.reset()
                self.__arancino.resumeArancinoThread()

                if result:
                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_RESET), 200
                else:  # when it is None means that no reset procedure is provided.
                    return self.__apiCreateErrorMessage(error_code=API_CODE.OK_RESET_NOT_PROVIDED), 500
            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 200
        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_RESET, internal_message=[None, str(ex)]), 500

    def enablePort(self, port_id):

        try:
            port = self.__arancino.findPort(port_id)

            if port:

                new_status = True
                curr_status = port.isEnabled()

                if new_status == curr_status:
                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_ALREADY_ENABLED), 200

                else:
                    port.setEnabled(new_status)
                    self.__synchronizer.writePortConfig(port)  # Note: maybe it's better wrapping this call inside Arancino class.

                    while not port.isConnected():
                        time.sleep(1)

                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_ENABLED), 200

            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 500

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def disablePort(self, port_id):
        # NOTE: in realta sono due operazioni: 1) disable 2) disconnect. Forse é il caso di dare due messaggi nella
        #   response, visto che il pacchetto JSON di ritorno prevede un array di messaggi e/o errori
        try:
            port = self.__arancino.findPort(port_id)

            if port:

                new_status = False
                curr_status = port.isEnabled()

                if new_status == curr_status:
                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_ALREADY_DISABLED), 200

                else:
                    port.setEnabled(new_status)
                    self.__synchronizer.writePortConfig(port)  # Note: maybe it's better wrapping this call inside Arancino class.

                    while port.isConnected():
                        time.sleep(1)

                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_DISABLED), 200

            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 500

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def uploadPortFirmware(self, port_id, firmware):
        try:
            port = self.__arancino.findPort(port_id)
            if port:

                self.__arancino.pauseArancinoThread()
                while not self.__arancino.isPaused():
                    pass
                result = port.upload(firmware)
                self.__arancino.resumeArancinoThread()

                if result:

                    rtn_cod = result[0]
                    std_out = result[1]
                    std_err = result[2]

                    if rtn_cod != 0:
                        return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_UPLOAD, internal_message=[std_out, std_err]), 500
                    else:
                        return self.__apiCreateOkMessage(response_code=API_CODE.OK_UPLOAD, internal_message=[std_out, std_err]), 201

                else:  # when it is None means that no uploaded procedure is provided.
                    return self.__apiCreateErrorMessage(error_code=API_CODE.OK_UPLOAD_NOT_PROVIDED), 500

            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 500
        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_UPLOAD, internal_message=[None, str(ex)]), 500

    def setPortConfig(self, port_id, config = None):
        try:

            if not config:
                return  self.__apiCreateErrorMessage(error_code=API_CODE.ERR_NO_CONFIG_PROVIDED), 500

            port = self.__arancino.findPort(port_id)
            
            if port:

                self.__arancino.pauseArancinoThread()

                if 'alias' in config:
                    curr_alias = port.getAlias()

                    if config['alias'] != curr_alias:
                        port.setAlias(config['alias'])
                        self.__synchronizer.writePortConfig(port)  # Note: maybe it's better wrapping this call inside Arancino class.
                        while not port.isConnected():
                            time.sleep(1)

                if 'enable' in config:
                    curr_status = port.isEnabled()
                    new_status = config['enable'].lower() == 'true'
                    if new_status != curr_status:
                        port.setEnabled(new_status)
                        self.__synchronizer.writePortConfig(port)  # Note: maybe it's better wrapping this call inside Arancino class.

                        while port.isConnected() != new_status:
                            time.sleep(1)

                if 'hide' in config:
                    curr_status = port.isHidden()
                    new_status = config['hide'].lower() == 'true'
                    if new_status != curr_status:
                        port.setHide(new_status)
                        self.__synchronizer.writePortConfig(port)  # Note: maybe it's better wrapping this call inside Arancino class.

                self.__arancino.resumeArancinoThread()

                return self.__apiCreateOkMessage(response_code=API_CODE.OK_CONFIGURATED), 200

            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 500

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def hidePort(self, port_id):
        try:
            port = self.__arancino.findPort(port_id)

            if port:

                new_status = True
                curr_status = port.isHidden()

                if new_status == curr_status:
                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_ALREADY_HIDDEN), 200

                else:
                    port.setHide(new_status)
                    self.__synchronizer.writePortConfig(port)  # Note: maybe it's better wrapping this call inside Arancino class.

                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_HIDDEN), 200

            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 500

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def showPort(self, port_id):
        try:
            port = self.__arancino.findPort(port_id)

            if port:

                new_status = False
                curr_status = port.isHidden()

                if new_status == curr_status:
                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_ALREADY_SHOWN), 200

                else:
                    port.setHide(new_status)
                    self.__synchronizer.writePortConfig(port)  # Note: maybe it's better wrapping this call inside Arancino class.

                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_SHOWN), 200

            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 500

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500

    def setArancinoConf(self, section, option, value):
        try:

            try:
                if section is None or section.strip() == "":
                    raise Exception("Configuration Section is empty")
            except Exception as ex:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_NO_ARANCINO_CONFIG_SECTION_PROVIDED, internal_message=[None, str(ex)]), 500

            try:
                if option is None or option.strip() == "":
                    raise Exception("Configuration Option is empty")
            except Exception as ex:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_NO_ARANCINO_CONFIG_OPTION_PROVIDED, internal_message=[None, str(ex)]), 500

            try:
                if value is None or value.strip() == "":
                    raise Exception("Configuration Value is empty")
            except Exception as ex:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_NO_ARANCINO_CONFIG_VALUE_PROVIDED, internal_message=[None, str(ex)]), 500

            CONF.set_config_by_name(section, option, value)

            return self.__apiCreateOkMessage(response_code=API_CODE.OK_ARANCINO_CONFIGURATED), 200

        except Exception as ex:
            LOG.error("Error on api call: {}".format(str(ex)))
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=[None, str(ex)]), 500


    #### UTILS ####
    def __getOsInfo(self):

        # default
        result = [system(), release()]

        try:
            cmd_arr = ["lsb_release", "-rds"]
            proc = subprocess.Popen(cmd_arr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            stdout = stdout.decode("utf-8")
            stderr = stderr.decode("utf-8")
            rtcode = proc.returncode

            if(rtcode == 0):
                result = stdout.strip().split('\n')

        except Exception as ex:
            pass

        finally:
            return result

    def __getNetwork(self):

        PROTO = netifaces.AF_INET  # We want only IPv4, for now at least

        # Get list of network interfaces
        ifaces = netifaces.interfaces()

        # Get addresses for each interface
        if_addrs = [(netifaces.ifaddresses(iface), iface) for iface in ifaces]

        # Filter for only IPv4 addresses
        if_inet_addrs = [(tup[0][PROTO], tup[1]) for tup in if_addrs if PROTO in tup[0]]

        all = []
        for item in if_inet_addrs:
            #if str(item[1]).upper() != "LO0":
                item[0][0]["iface"] = str(item[1])
                print(item[0][0])

                all.append(item[0][0])

        return all

    def __getListOfPortDiscovered(self):
        c = {}
        for id, port in self.__arancino.getDiscoveredPorts().items():
            if port.getPortType().name not in c:
                c[port.getPortType().name] = []
            c[port.getPortType().name].append(id)
        return c

    def __getListOfPortConnected(self):
        d = {}
        for id, port in self.__arancino.getConnectedPorts().items():
            if port.getPortType().name not in d:
                d[port.getPortType().name] = []
            d[port.getPortType().name].append(id)
        return d

    def __apiCreatePortResponse(self, port):
    #def __get_response_for_port(self, port=None):
        response = {

        }

        if port is not None:

            # BASE ARANCINO METADATA (B)Base
            response[DB_KEYS.B_ID] = port.getId()
            response[DB_KEYS.L_DEVICE] = port.getDevice()
            response[DB_KEYS.B_PORT_TYPE] = port.getPortType().name
            response[DB_KEYS.B_LIB_VER] = None if port.getLibVersion() is None else str(port.getLibVersion())
            response[DB_KEYS.B_FW_NAME] = None if port.getFirmwareName() is None else str(port.getFirmwareName())
            response[DB_KEYS.B_FW_VER] = None if port.getFirmwareVersion() is None else str(port.getFirmwareVersion())
            response[DB_KEYS.B_FW_UPLOAD_DATE] = None if port.getFirmwareUploadDate() is None else port.getFirmwareUploadDate()

            # BASE ARANCINO STATUS METADATA (S)Status
            response[DB_KEYS.S_CONNECTED] = port.isConnected()
            response[DB_KEYS.S_PLUGGED] = port.isPlugged()
            response[DB_KEYS.B_CREATION_DATE] = port.getCreationDate()
            response[DB_KEYS.S_LAST_USAGE_DATE] = port.getLastUsageDate()
            response[DB_KEYS.S_UPTIME] = None if port.getUptime() is None else secondsToHumanString(port.getUptime())
            response[DB_KEYS.S_COMPATIBILITY] = port.isCompatible()
            response[DB_KEYS.S_STARTED] = port.isStarted()

            # BASE ARANCINO CONFIGURATION METADATA (C)Configuration
            response[DB_KEYS.C_ENABLED] = port.isEnabled()
            response[DB_KEYS.C_ALIAS] = port.getAlias()
            response[DB_KEYS.C_HIDE_DEVICE] = port.isHidden()

            if port.getPortType() == PortTypes.SERIAL:
                response[DB_KEYS.P_VID] = port.getVID()
                response[DB_KEYS.P_PID] = port.getPID()
                response[DB_KEYS.P_NAME] = port.getName()
                response[DB_KEYS.P_DESCRIPTION] = port.getDescription()
                response[DB_KEYS.P_HWID] = port.getHWID()
                response[DB_KEYS.P_SERIALNUMBER] = port.getSerialNumber()
                response[DB_KEYS.P_LOCATION] = port.getLocation()
                response[DB_KEYS.P_MANUFACTURER] = port.getManufacturer()
                response[DB_KEYS.P_PRODUCT] = port.getProduct()
                response[DB_KEYS.P_INTERFACE] = port.getInterface()

            elif port.getPortType() == PortTypes.TEST:
                pass

        return response

    def __apiCreateErrorMessage(self, error_code=0, user_message=None, internal_message=None):

        if user_message is None:
            user_message = API_CODE.USER_MESSAGE(error_code)

        if internal_message is None:
            internal_message = [API_CODE.INTERNAL_MESSAGE(error_code)]

        return self.__apiCreateResponseMessage(return_code=error_code, user_message=user_message, internal_message=internal_message, isError=True)

    def __apiCreateOkMessage(self, response_code=0, user_message=None, internal_message=None):

        if user_message is None:
            user_message = API_CODE.USER_MESSAGE(response_code)

        if internal_message is None:
            internal_message = [API_CODE.INTERNAL_MESSAGE(response_code)]

        return self.__apiCreateResponseMessage(return_code=response_code, user_message=user_message, internal_message=internal_message, isError=False)

    def __apiCreateResponseMessage(self, return_code=0, user_message=None, internal_message=None, isError=False):

        return {
            "arancino": {
                "response": [
                    {
                        "isError": isError,
                        "userMessage": user_message,
                        "internalMessage": internal_message,
                        "returnCode": return_code
                    }]
            }
        }
