#!/usr/bin/env python3

import json
import sys

import usb.control
import usb.core
import usb.util

from serialCDCACM import check_is_CDCACM
from usblib import device_from_fd


def usb_info(fd):
    try:
        port = {}
        port['idVendor'] = None
        port['idProduct'] = None
        port['iManufacturer'] = None
        port['iProduct'] = None
        port['iSerialNumber'] = None
        dev = device_from_fd(fd)
        if check_is_CDCACM(dev):
            port['idVendor'] = dev.idVendor
            port['idProduct'] = dev.idProduct
            port['iManufacturer'] = dev.manufacturer
            port['iProduct'] = dev.product
            port['iSerialNumber'] = dev.serial_number
    except Exception as e:
        pass
    finally:
        print(json.dumps(port))


fd = int(sys.argv[1])
usb_info(fd)
