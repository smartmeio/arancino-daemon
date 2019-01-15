'''

Copyright ® SmartMe.IO  2018

LICENSE HERE

Filename: arancino_exceptions.py
Author: Sergio Tomasello - sergio@smartme.io
Date: 2018 01 15


'''


class InvalidArgumentsNumberException(Exception):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(InvalidArgumentsNumberException, self).__init__(message)

        # Now for your custom code...
        self.error_code = error_code


class InvalidCommandException(Exception):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(InvalidCommandException, self).__init__(message)

        # Now for your custom code...
        self.error_code = error_code


class RedisGenericException(Exception):
    def __init__(self, message, error_code):

        # Call the base class constructor with the parameters it needs
        super(RedisGenericException, self).__init__(message)

        # Now for your custom code...
        self.error_code = error_code

