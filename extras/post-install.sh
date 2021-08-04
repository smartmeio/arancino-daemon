#!/bin/bash

echo --------------------------------------
echo "Making Logs and Conf directories"
# create logs dir
mkdir -p /data/data/com.termux/files/usr/var/log/arancino
#mkdir -p "$ARANCINOLOG"

# create arancino dir
ARANCINO="/data/data/com.termux/files/usr/etc/arancino"
ARANCINOCONF="/data/data/com.termux/files/usr/etc/arancino/config"
mkdir -p "$ARANCINO"
mkdir -p "$ARANCINOCONF"

# mkdir -p /etc/redis/cwd
# chown -R redis:redis /etc/redis/cwd

echo --------------------------------------

echo --------------------------------------
echo "Backup previous configurations files...."
timestamp=$(date +%Y%m%d_%H%M%S)
[ -f $ARANCINOCONF/arancino.prod.cfg ] && mv $ARANCINOCONF/arancino.prod.cfg $ARANCINOCONF/arancino_$timestamp.cfg
[ -f $ARANCINOCONF/arancino.dev.cfg ] && mv $ARANCINOCONF/arancino.dev.cfg $ARANCINOCONF/arancino_$timestamp.dev.cfg
cp config/arancino.prod.cfg $ARANCINOCONF/arancino.prod.cfg
cp config/arancino.dev.cfg $ARANCINOCONF/arancino.dev.cfg
cp config/gunicorn.cfg.py $ARANCINOCONF/gunicorn.cfg.py

cp extras/vars.env $ARANCINO/vars.env

mkdir -p "$ARANCINO"/templates
cp templates/default.json.tmpl $ARANCINO/templates/default.json.tmpl
cp templates/default.xml.tmpl $ARANCINO/templates/default.xml.tmpl
cp templates/default.yaml.tmpl $ARANCINO/templates/default.yaml.tmpl
cp templates/S4T_default.json.tmpl $ARANCINO/templates/S4T_default.json.tmpl
echo --------------------------------------

echo --------------------------------------
echo "Giving grants 644 and copying services file"
chmod 644 $ARANCINOCONF/arancino.prod.cfg
chmod 644 $ARANCINOCONF/arancino.dev.cfg

#copy arancino service file to /ectc/systemd directory
mkdir -p $PREFIX/var/service/arancino/log
ln -sf $PREFIX/share/termux-services/svlogger $PREFIX/var/service/arancino/log/run
touch $PREFIX/var/service/arancino/run
cp extras/arancino.service $PREFIX/var/service/arancino/run
chmod +x $PREFIX/var/service/arancino/run

echo --------------------------------------

echo --------------------------------------
echo "Reloading daemons...."

#enable services
sv-enable arancino
sv up arancino

echo --------------------------------------

#echo --------------------------------------
#echo Resetting main microcontroller
##reset main mcu
#echo 0 > /sys/class/gpio/gpio25/value
#echo 1 > /sys/class/gpio/gpio25/value
#echo --------------------------------------