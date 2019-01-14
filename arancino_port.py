'''

Copyright ® SmartMe.IO  2018

LICENSE HERE

Author: Sergio Tomasello - sergio@smartme.io
Date: 2019 01 14

'''





class ArancinoPort:

    # serial port identification
    id = None

    # configuration metadata
    enabled = False
    autoreconnect = False
    alias = None

    # status metadata
    plugged = False
    connected = False
    datetime = None

    # serial port
    port = None


    def __init__(self, enabled = False, autoreconnect = False, alias = None, plugged = False, connected = False, port = None ):

        # serial port
        self.port = port

        # serial port identification
        self.id = port.serial_number

        # configuration metadata
        self.enabled = enabled
        self.autoreconnect = autoreconnect
        self.alias = alias

        # status metadata
        self.plugged = plugged
        self.connected = connected

        #todo datetime attribute


