#!/bin/bash

# create logs dir
#mkdir -p /var/log/arancino
mkdir -p $ARANCINOLOG

# create arancino dir
#mkdir -p /etc/arancino/config
mkdir -p $ARANCINOCONF

#change permissions to services files
chown 644 extras/arancino.service
chown 644 extras/redis-persistent.service
chown 644 extras/redis-volatile.service
chown 644 config/arancino.cfg

#copy arancino service file to /ectc/systemd directory
cp extras/arancino.service /etc/systemd/system/

#copy redis services files to /lib/systemd directory
cp extras/redis-*.service /lib/systemd/system/

#copy redis conf files
cp extras/*.conf /etc/redis/

#copy arancino config file to /etc/arancino/config <== ARANCINOCONF and make a backup of current conf file, if different
crc_new=$(md5sum config/arancino.cfg | awk {'print $1'})
crc_old=$(md5sum $ARANCINOCONF/arancino.cfg | awk {'print $1'})
timestamp=$(date +%Y%m%d_%H%M%S)

if [ "$crc_new" != "$crc_old" ]
then
    mv $ARANCINOCONF/arancino.cfg $ARANCINOCONF/arancino_$timestamp.cfg
    cp config/arancino.cfg $ARANCINOCONF/arancino.cfg
fi

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

#reset main mcu
echo 0 > /sys/class/gpio/gpio25/value
echo 1 > /sys/class/gpio/gpio25/value