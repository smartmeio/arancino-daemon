#!/usr/bin/env python3

import sys

import usb
import usb.control
import usb.core
import usb.util

from serialCDCACM import check_is_CDCACM, serial_CDCACM
from usblib import device_from_fd


def reset(fd):
    try:
        dev = device_from_fd(fd)

        baudrate = 300

        serial = None
        if check_is_CDCACM(dev):
            serial = serial_CDCACM(dev=dev, baudrate=baudrate)
            serial.close()

    except Exception as e:
        pass
        
    

fd = int(sys.argv[1])
reset(fd)
