import time

from arancino.Arancino import Arancino
from arancino.ArancinoUtils import ArancinoConfig, getProcessUptime
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

class ArancinoApi():

    def __init__(self):

        self.__arancino = Arancino()
        #self.__conf = ArancinoConfig.Instance()
        self.__synchronizer = ArancinoPortSynch()


    def resetPort(self, port_id):
        try:
            port = self.__arancino.findPort(port_id)

            if port:

                self.__arancino.pauseArancinoThread()
                result = port.reset()
                self.__arancino.resumeArancinoThread()

                if result:
                    return self.__apiCreateOkMessage(response_code=API_CODE.OK_RESET), 200
                else:  # when it is None means that no reset procedure is provided.
                    return self.__apiCreateErrorMessage(error_code=API_CODE.OK_RESET_NOT_PROVIDED), 500
            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 200
        except Exception as ex:
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_RESET, internal_message=str(ex)), 500


    def uploadFirmware(self, port_id, firmware):
        try:
            port = self.__arancino.findPort(port_id)
            if port:

                self.__arancino.pauseArancinoThread()
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
                    return self.__apiCreateErrorMessage(error_code=API_CODE.OK_RESET_NOT_PROVIDED), 500

            else:
                return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_PORT_NOT_FOUND), 500
        except Exception as ex:
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_UPLOAD, internal_message=str(ex)), 500


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
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=str(ex)), 500


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
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=str(ex)), 500


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
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=str(ex)), 500


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
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=str(ex)), 500


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
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=str(ex)), 500


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
                            "connected": ports_disc,
                            "discovered": ports_conn
                        }
                    }
                }
            }

            return response, 200

        except Exception as ex:
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=str(ex)), 500


    def hello(self):
        try:
            sys_upt = uptime()
            ara_upt = self.__arancino.getUptime()

            c = self.getPortsConnected()
            d = self.getPortsDiscovered()
            response = {
                "arancino": {
                    "system": {
                        "os" : [system(), release()],
                        "network": [gethostname(), gethostbyname(gethostname())],
                        "uptime": [sys_upt, getProcessUptime(int(sys_upt))]
                    },
                    "arancino": {
                        "uptime" : [ara_upt, getProcessUptime(int(ara_upt))],
                        "version": str(CONF.get_metadata_version()),
                        "ports": {
                            "discovered": d["arancino"]["arancino"]["ports"]["discovered"],
                            "connected": c["arancino"]["arancino"]["ports"]["connected"]
                        }
                    }
                }
            }

            return response, 200
        except Exception as ex:
            return self.__apiCreateErrorMessage(error_code=API_CODE.ERR_GENERIC, internal_message=str(ex)), 500


    def __apiCreatePortResponse(self, port):
    #def __get_response_for_port(self, port=None):
        response = {

        }

        if port is not None:

            # BASE ARANCINO METADATA (B)Base
            response[DB_KEYS.B_ID] = port.getId()
            response[DB_KEYS.B_DEVICE] = port.getDevice()
            response[DB_KEYS.B_PORT_TYPE] = port.getPortType().name
            response[DB_KEYS.B_LIB_VER] = str(port.getLibVersion())

            # BASE ARANCINO STATUS METADATA (S)Status
            response[DB_KEYS.S_CONNECTED] = port.isConnected()
            response[DB_KEYS.S_PLUGGED] = port.isPlugged()
            response[DB_KEYS.B_CREATION_DATE] = port.getCreationDate()
            response[DB_KEYS.S_LAST_USAGE_DATE] = port.getLastUsageDate()

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
            internal_message = API_CODE.INTERNAL_MESSAGE(error_code)

        return {
            "arancino": {
                "errors": [
                    {
                        "userMessage": user_message,
                        "internalMessage": internal_message,
                        "returnCode": error_code
                    }]
            }
        }


    def __apiCreateOkMessage(self, response_code=0, user_message=None, internal_message=None):

        if user_message is None:
            user_message = API_CODE.USER_MESSAGE(response_code)

        if internal_message is None:
            internal_message = API_CODE.INTERNAL_MESSAGE(response_code)

        return {
            "arancino": {
                "messages": [
                    {
                        "userMessage": user_message,
                        "internalMessage": internal_message,
                        "returnCode": response_code
                    }]
            }
        }