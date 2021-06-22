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

from arancino.ArancinoConstants import *
from arancino.ArancinoExceptions import *

#TODO make a super class ArancinoCortexPacket with abstract method to be implemented:
# - get id
# - get arguments
# - init (raw command)
# - init (id, args)
# - get raw


class ArancinoComamnd:

    def __init__(self, raw_command=None, cmd_id=None, cmd_args=None):

        if isinstance(raw_command, str):
            self.__constructorA(raw_command=raw_command)

        elif isinstance(cmd_id, str) and isinstance(cmd_args, list):
            self.__constructorB(cmd_id=cmd_id, cmd_args=cmd_args)


    def __constructorA(self, raw_command=None):
        """
        Create an Arancino Comamnd starting from a Raw Command
        :param raw_command:
        """
        self.__raw = raw_command

        cmd_parsed = self.__parseCommand(raw_command)

        #self.__id = cmd_parsed[0]       # first element is the Command Identifier
        #self.__args = cmd_parsed[1]     # second element is the array of Command Arguments

        if self.__isCmdIdAvailable(cmd_parsed[0]):
            self.__id = cmd_parsed[0]
        else:
            raise InvalidCommandException("Command does not exist: " + cmd_parsed[0] + " - Skipped", ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)

        try:
            self.__args = self.__checkAndGetArgsByCmdId(cmd_parsed[0], cmd_parsed[1])
        except InvalidArgumentsNumberException as ex:
            raise ex


    def __constructorB(self, cmd_id=None, cmd_args=None):
        """
        Create an Arancino Comamnd starting from a Command Identifier and Command Arguments
        :param cmd_id: {String} Command Identifier
        :param cmd_args: {Array of String} Command Arguments
        """
        if self.__isCmdIdAvailable(cmd_id):
            self.__id = cmd_id
        else:
            raise InvalidCommandException("Command does not exist: " + cmd_id + " - Skipped", ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)


        try:
            self.__args = self.__checkAndGetArgsByCmdId(cmd_id, cmd_args)
        except InvalidArgumentsNumberException as ex:
            raise ex



        # if n_args_required == n_args:
        #     self.__args = cmd_args
        # else:
        #     raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + n_args + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)


        self.__raw = self.__id + ArancinoSpecialChars.CHR_SEP + ArancinoSpecialChars.CHR_SEP.join(self.__args) + ArancinoSpecialChars.CHR_EOT


    def getId(self):
        return self.__id


    def getArguments(self):
        return self.__args


    def getRaw(self):
        return self.__raw


    def __parseCommand(self, raw_command):
        '''
        From the raw command it separates the Command Identifier and Command Arguments,
            making check about the command id and the number of arguments.

        :param raw_command: The raw command sent by the mcu, including cortex protocol special chars.
        :return: {String} Command Id, {Array} Command Arguments.
        '''

        # remove trailing blank chars if there are
        raw_command = raw_command.strip()

        # splits command by separator char
        cmd = raw_command.strip(ArancinoSpecialChars.CHR_EOT).split(ArancinoSpecialChars.CHR_SEP)

        if len(cmd) > 0:
            cmd_id = cmd[0]
            idx = len(cmd)
            cmd_args = cmd[1:idx]

            return cmd_id, cmd_args
        else:
            return None


        # if len(cmd) > 0:
        #
        #     # get the command id (identifier)
        #     cmd_id = cmd[0]
        #
        #     if self.__isCmdIdAvailable(cmd_id):
        #         # command id is in the list:
        #         # now retrieve command arguments
        #         idx = len(cmd)
        #         cmd_args = cmd[1:idx]
        #
        #         # retrieve the number of arguments required for the command
        #         n_args_required = self.__getArgsNumberByCmdId(cmd_id)
        #         n_args = len(cmd_args)
        #
        #         if n_args_required == n_args:
        #             return cmd_id, cmd_args
        #
        #         else:
        #             raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)
        #
        #     else:
        #         raise InvalidCommandException("Command does not exist: " + cmd_id + " - Skipped", ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)
        #
        # else:
        #     raise InvalidCommandException("No command received", ArancinoCommandErrorCodes.ERR_CMD_NOT_RCV)


    def __isCmdIdAvailable(self, cmd_id):
        '''
        Check if the Command Identifier is in the list of the defined comamnds.

        :param cmd_id: {String} the Command Identifier.
        :return: {Bool} True if exist, False if not.
        '''

        if cmd_id in ArancinoCommandIdentifiers.COMMANDS_LIST:
            return True
        else:
            return False


    def __getArgsNumberByCmdId(self, cmd_id):
        '''
        Get the number of Argument for the specified Command Identifier.

        :param cmd_id: {String} the Command identifier.
        :return: {Integer} the number of arguments for the specified Command Identifier.
        '''

        # command = ArancinoCommandIdentifiers.COMMANDS_DICT[cmd_id]
        # num = command["args"]
        # op = command["op"]

        command = ArancinoCommandIdentifiers.COMMANDS_DICT[cmd_id]
        num = command["args"]
        num2 = command["args2"] if "args2" in command else None
        op = command["op"]


        #return num, op

        return num, num2, op


    def __checkAndGetArgsByCmdId(self, cmd_id, cmd_args):
        # retrieve the number of arguments required for the command
        # res = self.__getArgsNumberByCmdId(cmd_id)
        # n_args_required = res[0]
        # n_args_operator = res[1]
        # n_args = len(cmd_args)

        # retrieve the number of arguments required for the command
        res = self.__getArgsNumberByCmdId(cmd_id)
        n_args_required = res[0]  # inferior edge
        n_args_required_2 = res[1]  # superior edge
        n_args_operator = res[2]
        n_args = len(cmd_args)

        if n_args_operator == ArancinoOperators.EQUAL:

            if n_args == n_args_required:
               return cmd_args
            else:
                raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: == (Equal) " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

        elif n_args_operator == ArancinoOperators.GREATER_THAN:
            if n_args > n_args_required:
                return cmd_args
            else:
                raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: > (Greater Than) " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

        elif n_args_operator == ArancinoOperators.GREATER_THAN_OR_EQUAL:
            if n_args >= n_args_required:
                return cmd_args
            else:
                raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: >= (Greater Than or Equal) " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

        elif n_args_operator == ArancinoOperators.LESS_THAN:
            if n_args < n_args_required:
                return cmd_args
            else:
                raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: < (Less Than) " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

        elif n_args_operator == ArancinoOperators.LESS_THAN_OR_EQUAL:
            if n_args <= n_args_required:
                return cmd_args
            else:
                raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: <= (Less Than or Equal) " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

        elif n_args_operator == ArancinoOperators.NOT_EQUAL:
            if n_args != n_args_required:
                return cmd_args
            else:
                raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: != (Not Equal) " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)

        elif n_args_operator == ArancinoOperators.BETWEEN:
            if n_args >= n_args_required and n_args <= n_args_required_2:
                return cmd_args
            else:
                raise InvalidArgumentsNumberException("Invalid arguments number for command " + cmd_id + ". Received: " + str(n_args) + "; Required: != (Between) " + str(n_args_required) + " and " + str(n_args_required_2) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)


class ArancinoResponse:

    def __init__(self, raw_response=None, rsp_id=None, rsp_args=None):

        if isinstance(raw_response, str):
            self.__constructorA(raw_response=raw_response)

        elif isinstance(rsp_id, str) and isinstance(rsp_args, list):
            self.__constructorB(rsp_id=rsp_id, rsp_args=rsp_args)


    def __constructorA(self, raw_response=None):
        self.__raw = raw_response

        rsp_parsed = self.__parseResponse(raw_response)

        self.__id = rsp_parsed[0]  # first element is the Response Code
        self.__args = rsp_parsed[1]  # second element is the array of Response Arguments


    def __constructorB(self, rsp_id=None, rsp_args=None):
        if self.__isRspIdAvailable(rsp_id):
            self.__id = rsp_id
        else:
            raise InvalidCommandException("Response does not exist: " + rsp_id + " - Skipped", ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)

        self.__args = rsp_args if len(rsp_args) > 0 else []

        self.__raw = self.__id + ArancinoSpecialChars.CHR_SEP + ArancinoSpecialChars.CHR_SEP.join(self.__args) + ArancinoSpecialChars.CHR_EOT


    def getId(self):
        return self.__id


    def getArguments(self):
        return self.__args


    def getRaw(self):
        return self.__raw


    def __parseResponse(self, raw_response):
        '''
        From the Raw Response it separates the Response Identifier and Response Arguments,
            making check about the command id and the number of arguments.

        :param raw_response: The raw command sent by the mcu, including cortex protocol special chars.
        :return: {String} Command Id, {Array} Command Arguments.
        '''

        # remove trailing blank chars if there are
        raw_response = raw_response.strip()

        # splits command by separator char
        rsp = raw_response.strip(ArancinoSpecialChars.CHR_EOT).split(ArancinoSpecialChars.CHR_SEP)

        if len(rsp) > 0:

            # get the response id (identifier)
            rsp_id = rsp[0]

            if self.__isRspIdAvailable(rsp_id):
                # Response Code is in the list:
                # now retrieve command arguments

                idx = len(rsp)
                rsp_args = rsp[1:idx]

            #     # retrieve the number of arguments required for the command
            #     n_args_required = self.__get_args_nr_by_cmd_id(rsp_id)
            #     n_args = len(cmd_args)
            #
            #     if n_args_required == n_args:
                return rsp_id, rsp_args
            #
            #     else:
            #         raise InvalidArgumentsNumberException("Invalid arguments number for command " + rsp_id + ". Received: " + n_args + "; Required: " + str(n_args_required) + ".", ArancinoCommandErrorCodes.ERR_CMD_PRM_NUM)
            #
            else:
                raise InvalidCommandException("Response does not exist: " + rsp_id + " - Skipped", ArancinoCommandErrorCodes.ERR_CMD_NOT_FND)

        else:
            raise InvalidCommandException("No command received", ArancinoCommandErrorCodes.ERR_CMD_NOT_RCV)


    def __isRspIdAvailable(self, rsp_id):
        '''
        Check if the Response Code is in the list of the defined Responses.

        :param rsp_id: {String} the Command Identifier.
        :return: {Bool} True if exist, False if not.
        '''

        if rsp_id in ArancinoCommandErrorCodes.ERRORS_CODE_LIST or rsp_id in ArancinoCommandResponseCodes.RESPONSES_CODE_LIST:
            return True
        else:
            return False
    
    def addChallenge(self, challenge):
        self.__args.append(challenge)

    
    def retrieveChallenge(self):
        return self.__args[len(self.__args)-1]
