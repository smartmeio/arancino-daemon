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
        if dev.is_kernel_driver_active(1):
            try:
                dev.detach_kernel_driver(1)
                print("kernel driver detached")
            except usb.core.USBError as e:
                sys.exit("Could not detach kernel driver: %s" % str(e))
        else:
            print("no kernel driver attached")

        if dev.is_kernel_driver_active(0):
            try:
                dev.detach_kernel_driver(0)
                print("kernel driver detached")
            except usb.core.USBError as e:
                sys.exit("Could not detach kernel driver: %s" % str(e))
        else:
            print("no kernel driver attached")


        if check_is_CDCACM(dev):
            serial = serial_CDCACM(dev=dev, baudrate=baudrate)
            print("depo init")
            serial.close()
            print("serial closed")

    except Exception as e:
        pass

        
    

fd = int(sys.argv[1])
reset(fd)
