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
fi

# echo out > /sys/class/gpio/gpio25/direction
# echo 1 > /sys/class/gpio/gpio25/value

sleep 3

# Arduino 1200 baud trick
stty -F $1 1200
sleep 3

port=($(echo "$1" | tr '/' '\n'))

# bossac actual upload
echo "upload port is $1"
bossac -i -d --port=${port[1]} -U true -i -e -w -v /tmp/sketch.bin -R

rc=$?

rm /tmp/sketch.bin

# echo in > /sys/class/gpio/gpio25/direction

exit $rc