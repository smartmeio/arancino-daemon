# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2019 SmartMe.IO

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

class ArancinoException(Exception):
    def __init__(self, message, error_code):
        # Call the base class constructor with the parameters it needs
        super(ArancinoException, self).__init__(message, error_code)

        # Now for your custom code...
        self.error_code = error_code

class InvalidArgumentsNumberException(ArancinoException):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(InvalidArgumentsNumberException, self).__init__(message, error_code)

        self.title = "The number of arguments sent with the command is not correct"
        self.message = message

        # Now for your custom code...
        #self.error_code = error_code


class InvalidCommandException(ArancinoException):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(InvalidCommandException, self).__init__(message, error_code)

        self.title = "The command sent is not a valid command."
        self.message = message

        # Now for your custom code...
        #self.error_code = error_code


class RedisGenericException(ArancinoException):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(RedisGenericException, self).__init__(message, error_code)

        self.title = "Redis error."
        self.message = message

        # Now for your custom code...
        #self.error_code = error_code


class RedisPersistentKeyExistsInStadardDatastoreException(ArancinoException):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(RedisPersistentKeyExistsInStadardDatastoreException, self).__init__(message, error_code)

        self.title = "Desired key already exists in the standard data store."
        self.message = message

        # Now for your custom code...
        #self.error_code = error_code


class RedisStandardKeyExistsInPersistentDatastoreException(ArancinoException):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(RedisStandardKeyExistsInPersistentDatastoreException, self).__init__(message, error_code)

        self.title = "Desired key already exists in the persistent data store."
        self.message = message
        # Now for your custom code...
        #self.error_code = error_code


class NonCompatibilityException(ArancinoException):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(NonCompatibilityException, self).__init__(message, error_code)

        self.title = "Daemon and Library are not compatible, please check compatibility matrix."
        self.message = message
        # Now for your custom code...
        #self.error_code = error_code

class NotImplemented(ArancinoException):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(NotImplemented, self).__init__(message, error_code)
        self.title = "Function not implemented."
        self.message = message

        # Now for your custom code...
        #self.error_code = error_code