#!/bin/bash -x
# Creation Date 2020.03.18
# Authors: sergio tomasello <sergio@smartme.io>
#          arturo rinaldi <arturo@smartme.io>

# Hex2bin conversion if needed
if [[ "${2##*.}" = "hex" ]]; then
  mv $2 /tmp/sketch.hex
  hex2bin /tmp/sketch.hex
  rm /tmp/sketch.hex
elif [[ "${2##*.}" = "bin" ]]; then
  mv $2 /tmp/sketch.bin
elif [[ "${2##*.}" = "zip" ]]; then
  mv $2 /tmp/sketch.zip
fi

# LOCALES
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# echo out > /sys/class/gpio/gpio25/direction
# echo 1 > /sys/class/gpio/gpio25/value

sleep 3

# Arduino 1200 baud trick
stty -F $1 1200
sleep 3

port=${1}

# nRF52 actual upload
echo "upload port is $1"
adafruit-nrfutil --verbose dfu serial -pkg "/tmp/sketch.zip" -p ${port} -b 115200 --singlebank

rc=$?

rm /tmp/sketch.zip

# echo in > /sys/class/gpio/gpio25/direction

exit $rc