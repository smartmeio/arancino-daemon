#!/bin/bash

source extras/vars.env


echo ---------Making Logs and Conf directories--------
# create logs dir
echo creating directory: $ARANCINO
mkdir -p $ARANCINO

# create arancino dir
#mkdir -p /etc/arancino/config
echo creating directory: $ARANCINOCONF
mkdir -p $ARANCINOCONF

#mkdir -p /etc/arancino/templates
echo creating directory: $ARANCINO/templates
mkdir -p $ARANCINO/templates

# create logs dir
echo creating directory: $ARANCINOLOG
mkdir -p $ARANCINOLOG

echo creating directory: /etc/redis/cwd
mkdir -p /etc/redis/cwd
chown -R redis:redis /etc/redis/cwd

echo -------------------------------------------------

echo ---Giving grants 644 and copying services file---
chown 644 extras/arancino.service
chown 644 config/arancino.cfg

cp extras/arancino.service /etc/systemd/system/
cp extras/vars.env /etc/arancino/
echo -------------------------------------------------


echo ------Backup previous configurations files-------
echo Backup previous configurations files
timestamp=$(date +%Y%m%d_%H%M%S)
[ -f /etc/arancino/config/arancino.cfg ] && mv $ARANCINOCONF/arancino.cfg $ARANCINOCONF/arancino_$timestamp.cfg
echo -------------------------------------------------

echo -------------------Copy files--------------------
cp config/arancino.cfg $ARANCINOCONF/arancino.cfg
cp config/gunicorn.cfg.py $ARANCINOCONF/gunicorn.cfg.py

cp templates/default.json.tmpl $ARANCINO/templates/default.json.tmpl
cp templates/default.xml.tmpl $ARANCINO/templates/default.xml.tmpl
cp templates/default.yaml.tmpl $ARANCINO/templates/default.yaml.tmpl
cp templates/S4T_default.json.tmpl $ARANCINO/templates/S4T_default.json.tmpl
echo -------------------------------------------------

echo ----Restoring redis databases to default number---
sed -i 's/databases 6/databases 16/g' /etc/redis/redis-volatile.conf
sed -i 's/databases 6/databases 16/g' /etc/redis/redis-persistent.conf

echo -------------Reloading daemons--------------------
systemctl daemon-reload

systemctl restart redis-volatile
systemctl restart redis-persistent
systemctl enable arancino
systemctl restart arancino
echo -------------------------------------------------
