#!/bin/bash

echo --------------------------------------
echo Making Logs and Conf directories
# create logs dir
mkdir -p /var/log/arancino
#mkdir -p "$ARANCINOLOG"

# create arancino dir
mkdir -p /etc/arancino/config
#mkdir -p "$ARANCINOCONF"
echo --------------------------------------

echo --------------------------------------
echo Giving grants 644 and copying services file
#change permissions to services files
chown 644 extras/arancino.service
#chown 644 extras/redis-persistent.service
#chown 644 extras/redis-volatile.service
chown 644 config/arancino.cfg

#copy arancino service file to /ectc/systemd directory
cp extras/arancino.service /etc/systemd/system/

#copy redis services files to /lib/systemd directory
#cp extras/redis-*.service /lib/systemd/system/

#copy redis conf files
#cp extras/*.conf /etc/redis/
echo --------------------------------------

echo --------------------------------------
echo Checking diff of configuration file and making a backup
#copy arancino config file to /etc/arancino/config <== ARANCINOCONF and make a backup of current conf file, if different
crc_new=$(md5sum config/arancino.cfg | awk {'print $1'})
crc_old=$(md5sum /etc/arancino/config/arancino.cfg | awk {'print $1'})
timestamp=$(date +%Y%m%d_%H%M%S)

if [ "$crc_new" != "$crc_old" ]
then
    echo Creating configuration backup file "/etc/arancino/config/arancino_$timestamp.cfg"
    mv /etc/arancino/config/arancino.cfg /etc/arancino/config/arancino_$timestamp.cfg
    cp config/arancino.cfg /etc/arancino/config/arancino.cfg
fi
echo --------------------------------------

echo --------------------------------------
echo Reloading daemons

#daemon reload
systemctl daemon-reload

#enable services
systemctl enable redis-volatile
systemctl enable redis-persistent
systemctl enable arancino

#start services
systemctl start redis-volatile
systemctl start redis-persistent
systemctl start arancino
echo --------------------------------------

#echo --------------------------------------
#echo Resetting main microcontroller
##reset main mcu
#echo 0 > /sys/class/gpio/gpio25/value
#echo 1 > /sys/class/gpio/gpio25/value
#echo --------------------------------------