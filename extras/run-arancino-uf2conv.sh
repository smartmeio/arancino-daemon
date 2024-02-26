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
elif [[ "${2##*.}" = "uf2" ]]; then
  mv $2 /tmp/sketch.uf2
fi

# echo out > /sys/class/gpio/gpio25/direction
# echo 1 > /sys/class/gpio/gpio25/value

sleep 3

# Arduino 1200 baud trick inside python script
port=$1

# u2fconv.py actual upload
echo "upload port is $1"

# actual upload command
/usr/bin/python3 -I /usr/bin/uf2conv.py --serial ${port} --family RP2040 --deploy /tmp/sketch.uf2

# alternative upload command with env variables
# $(which python3) -I $(which uf2conv.py) --serial ${port} --family RP2040 --deploy /tmp/sketch.uf2

rc=$?

rm /tmp/sketch.uf2

# echo in > /sys/class/gpio/gpio25/direction

exit $rc