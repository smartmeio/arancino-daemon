#!/bin/bash

# loads vars from file
source extras/arancino.env

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

#copy arancino config file to /etc/arancino/config <== ARANCINOCONF
cp config/arancino.cfg $ARANCINOCONF

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
