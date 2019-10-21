#!/bin/bash

#change permissions to services files
chown 644 extras/arancino.service
chown 644 extras/redis-persistent.service
chown 644 extras/redis-volatile.service

#move services files to systemd directory
cp extras/*.service /etc/systemd/system/

#move redis conf files
cp extras/*.conf /etc/redis/


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
