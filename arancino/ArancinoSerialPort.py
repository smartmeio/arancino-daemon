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

import serial, time
from types import FunctionType
from arancino.ArancinoPort import ArancinoPort, PortTypes
from arancino.ArancinoSerialHandler import ArancinoSerialHandler
from arancino.ArancinoCortex import *
from arancino.ArancinoUtils import ArancinoLogger
from arancino.ArancinoCommandExecutor import ArancinoCommandExecutor

LOG = ArancinoLogger.Instance().get_logger()

class ArancinoSerialPort(ArancinoPort):

    def __init__(self, port_info=None, device=None, baudrate=9600, m_s_plugged=False, m_c_enabled=True, m_c_auto_connect=True, m_c_alias="", m_c_hide=False, received_command_handler=None, disconnection_handler=None, timeout=None):

        self.port_type = PortTypes.Serial

        self.__serial_port = None       # type: serial.Serial
        self.__port_info = port_info    # type: serial.tools.ListPortInfo
        self.__device = device          # the plugged tty i.e: /dev/tty.ACM0

        self.__id = None  # Id is the Serial Number. It will have a value when the Serial Port is connected


        # SERIAL PORT PARAMETER
        self.__baudrate = baudrate
        # self.__bytesize = bytesize
        # self.__parity = parity
        # self.__stopbits = stopbits
        self.__timeout = timeout
        # self.__xonxoff = xonxoff
        # self.__rtscts = rtscts
        # self.__write_timeout = write_timeout
        # self.__dsrdtr = dsrdtr
        # self.__inter_byte_timeout = inter_byte_timeout
        # self.__exclusive = exclusive

        # ARANCINO PORT METADATA
        self.__m_p_vid = None
        self.__m_p_pid = None
        self.__m_p_name = None
        self.__m_p_description = None
        self.__m_p_hwid = None
        self.__m_p_serial_number = None
        self.__m_p_location = None
        self.__m_p_manufacturer = None
        self.__m_p_product = None
        self.__m_p_interface = None
        #self.__m_p_device = None

        #self.__populate_port_info(device=self.__device)
        self.__populate_port_info(device=self.__device, port_info=self.__port_info)

        self.__log_prefix = "[" + self.__id + " => " + self.__device + "] "

        # Command Executor
        self.__executor = ArancinoCommandExecutor(self.__id, self.__device)

        # ARANCINO STATUS METADATA
        self.__m_s_plugged = m_s_plugged   # TODO: questo forse non serve, perche se é l'istanza di questo oggetto esiste sicuramente é plugged. quando la porta viene staccata fisicamente, l'istanza non ha motivo di esistere
        self.__m_s_connected = False

        # ARANCINO CONFIGURATION METADATA
        self.__m_c_enabled = m_c_enabled
        self.__m_c_auto_connect = m_c_auto_connect
        self.__m_c_alias = m_c_alias
        self.__m_c_hide = m_c_hide

        # CALLBACK FUNCTIONS
        self.set_received_command_handler(received_command_handler)  # this is the handler to be used to receive an ArancinoCommand and exec that command.
        self.set_disconnection_handler(disconnection_handler)  # this is the handler to be used whene a disconnection event is triggered


    def __command_received_handler(self, raw_command):
        """
        This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
            It first receives a Raw Command from the Serial Port, then translate it to an ArancinoCommand object
            and send it back to another callback function

        :param raw_command: the Raw Command received from the Serial port
        :return: void.
        """
        try:
            # create an Arancino Comamnd from the raw command
            acmd = ArancinoComamnd(raw_command=raw_command)
            LOG.debug("{}Received: {}: {}".format(self.__log_prefix, acmd.get_id(), str(acmd.get_arguments())))

            # check if the exec command handler callback function is defined
            if self.__received_command_handler is not None:
                self.__received_command_handler(self.__id + " - " + self.__device, acmd)

            # call the Command Executor and get a raw response
            raw_response = self.__executor.exec(acmd)

            # create the Arancino Response object
            arsp = ArancinoResponse(raw_response=raw_response)
            LOG.debug("{}Sending: {}: {}".format(self.__log_prefix, arsp.get_id(), str(arsp.get_arguments())))

            # send the response back.
            self.__serial_port.write(raw_response.encode())

        except Exception as ex:
            raise ex


    def __connection_lost_handler(self):
        """
        This is an Asynchronous function, and represent "handler" to be used by ArancinoSerialHandeler.
            It is triggered when the connection is closed then calls another callback function.

        :return: void
        """
        # TODO se la disconnessione viene gestita al livello superiore facendo una del
        #  di questo oggetto non ha senso impostare connected = false e via dicendo

        self.__m_s_connected = False

        # free the handler and serial port
        self.__serial_port.close()

        del self.__serial_handler
        del self.__serial_port

        LOG.warning("{}Serial port closed.".format(self.__log_prefix))

        # check if the disconnection handler callback function is defined
        if self.__disconnection_handler is not None:
            self.__disconnection_handler(self.__id + " - " + self.__device)
        else:  # do nothing
            pass


    def send_response(self, response):
        """
        Send a Response to the mcu. A Response is bind to a Command. The Response is sent only if the
            Serial Port is Connected.

        :param response: {String} The Response to send back to the MCU.
        :return: void
        """

        if self.__m_s_connected:
            self.__serial_port.write(response.encode())
        else:  # not connected
            #TODO: LOG or EXCEPTION
            print("port not connected")
            pass


    def connect(self):
        try:
            # check if the device is enabled and not already connected
            if self.__m_c_enabled:
                if not self.__m_s_connected :
                    try:

                        # first resetting
                        self.reset()


                        LOG.info("{}Connecting...".format(self.__log_prefix))
                        self.__serial_port = serial.Serial(None, self.__baudrate, timeout=self.__timeout)
                        self.__serial_port.port = self.__device
                        self.__serial_port.open()

                        # TODO define a name for Serial Handler Thread
                        self.__serial_handler = ArancinoSerialHandler("ArancinoSerialHandler", self.__serial_port, self.__id, self.__m_p_device , self.__command_received_handler, self.__connection_lost_handler)
                        self.__m_s_connected = True
                        self.__serial_handler.start()
                        LOG.info("{}Connected".format(self.__log_prefix))

                    except Exception as ex:
                        # TODO LOG SOMETHING OR NOT?
                        print(ex)
                        raise ex

                else:
                    # TODO LOG or EXCPETION
                    print("port already connected")
                    pass
            else: # not enabled
                #TODO LOG or EXCEPTION
                print("port not enabled")
                pass

        except Exception as ex:
            raise ex


    def disconnect(self):
        try:
            # check if the device is already
            if self.__m_s_connected:
                self.__m_s_connected = False

                self.__serial_handler.stop()


                # unsets the Port Metadata
                # self.__m_p_vid = None
                # self.__m_p_pid = None
                # self.__m_p_name = None
                # self.__m_p_description = None
                # self.__m_p_hwid = None
                # self.__m_p_serialnumber = None
                # self.__m_p_location = None
                # self.__m_p_manufacturer = None
                # self.__m_p_product = None
                # self.__m_p_interface = None
                # self.__id = None
                # self.__device = None
            else:
                # TODO LOG or EXCEPTION
                LOG.debug("{}Already Disconnected".format(self.__log_prefix))
                pass

        except Exception as ex:
            raise ex


    def reset(self):
        try:
            # touch to reset
            ser = serial.Serial()
            ser.baudrate = 300 # TODO make it an attribute
            ser.port = self.__device
            ser.open()
            ser.close()
            del ser
            time.sleep(3)
        except Exception as ex:
            #LOG.info("{}Connected".format(self.__log_prefix))
            LOG.exception(self.__log_prefix + str(ex))


    def __populate_port_info(self, device=None, port_info=None):
        try:
            if device is not None:
                p = self.__find_port_info(device=device)
            elif port_info is not None:
                p = port_info
            else:
                raise Exception("Cannot create Arancino Serial Port: Device and Port Info are None, please fill one of them")


            # from serial.tools import list_ports
            # ports = list_ports.comports()
            # for p in ports:
            #     if p.device == device:
                    # sets Port Metadata
            self.__m_p_vid = str(hex(p.vid))
            self.__m_p_pid = str(hex(p.pid))
            self.__m_p_name = p.name
            self.__m_p_description = p.description
            self.__m_p_hwid = p.hwid
            self.__m_p_serial_number = p.serial_number
            self.__m_p_location = p.location
            self.__m_p_manufacturer = p.manufacturer
            self.__m_p_product = p.product
            self.__m_p_interface = p.interface
            self.__device = p.device

            self.__id = p.serial_number

                    # break  # break the whole loop

        except Exception as ex:
            raise ex


    def __find_port_info(self, device=None):
        from serial.tools import list_ports
        ports = list_ports.comports()
        for p in ports:
            if p.device == device:
                return p


    # ENCAPSULATORS

    def get_id(self):
        return self.__id


    def get_enabled(self):
        return self.__m_c_enabled


    def get_auto_connect(self):
        return self.__m_c_auto_connect


    def get_alias(self):
        return self.__m_c_alias


    def get_hide(self):
        return self.__m_c_hide


    def get_vid(self):
        return self.__m_p_vid


    def get_pid(self):
        return self.__m_p_pid


    def get_name(self):
        return self.__m_p_name


    def get_description(self):
        return self.__m_p_description


    def get_hwid(self):
        self.__m_p_hwid


    def get_serial_number(self):
        return self.__m_p_serial_number


    def get_location(self):
        return self.__m_p_location


    def get_manufacturer(self):
        return self.__m_p_manufacturer


    def get_product(self):
        return self.__m_p_product


    def get_interface(self):
        return self.__m_p_interface


    def get_device(self):
            return self.__device


    def get_plugged(self):
        return self.__m_s_plugged


    def get_connected(self):
        return self.__m_s_connected


    def set_enabled(self, enabled):
        self.__m_c_enabled = enabled


    def set_auto_connect(self, auto_connect):
        self.__m_c_auto_connect = auto_connect


    def set_alias(self, alias):
        self.__m_c_alias = alias


    def set_hide(self, hide):
        self.__m_c_hide = hide


    def set_disconnection_handler(self, disconnection_handler):
        if isinstance(disconnection_handler, FunctionType):
            self.__disconnection_handler = disconnection_handler
        else:
            self.__disconnection_handler = None


    def set_received_command_handler(self, received_command_handler):
        if isinstance(received_command_handler, FunctionType):
            self.__received_command_handler = received_command_handler
        else:
            self.__received_command_handler = None

