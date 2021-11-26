#!/usr/bin/env python3

import sys

import redis
import usb
import usb.control
import usb.core
import usb.util

from serialCDCACM import check_is_CDCACM, serial_CDCACM
from usblib import device_from_fd

serial = None

def connectRedis():
    host = 'localhost'
    port = 6379
    db = 0

    cl = redis.Redis(host, port, db)
    return cl

def sendResponse(message):
    global serial
    try:
        serial.write(message['data'])
    except Exception as e:
        pass


def main(fd):
    try:
        global serial
        dev = device_from_fd(fd)
        redisClient = connectRedis()
        sub_topic = dev.serial_number + '_response'
        pub_topic = dev.serial_number + '_command'

        # Configure usb-serial-converter
        baudrate = 4000000 # From environment variable

        serial = None
        if dev.is_kernel_driver_active(0):
            try:
                dev.detach_kernel_driver(0)
                print("kernel driver detached")
            except usb.core.USBError as e:
                sys.exit("Could not detach kernel driver: %s" % str(e))
        else:
            print("no kernel driver attached")
            
        if dev.is_kernel_driver_active(1):
            try:
                dev.detach_kernel_driver(1)
                print("kernel driver detached")
            except usb.core.USBError as e:
                sys.exit("Could not detach kernel driver: %s" % str(e))
        else:
            print("no kernel driver attached")

        if check_is_CDCACM(dev):
            print("serialDaemon:: Connected device is DCDACM")
            serial = serial_CDCACM(dev=dev, baudrate=baudrate)

        p = redisClient.pubsub()
        p.subscribe(**{sub_topic: sendResponse})
        p.run_in_thread(sleep_time=0.001)


        if serial:
            serial.purge() # clear whatever the printer has sent while octoprint wasn't connected

            databuf = b'' # Buffer to split received bytes into lines for octoprint's readline()
            while True:

                databuf += serial.read(1024,1000)
                if chr(4).encode() in databuf:
                    command, databuf = databuf.split(chr(4).encode(), 1)
                    serial.purge()
                    databuf = b''
                    print(command)
                    redisClient.publish(pub_topic, command)
                    del(command)
    except Exception as e:
        print(e.with_traceback(tb))
        redisClient.publish(pub_topic, 'disconnected')
        
    

fd = int(sys.argv[1])
main(fd)
