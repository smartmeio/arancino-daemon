#!/bin/bash
echo ---Stopping and disabling services and daemons---
#stop services (first arancino then redis)
systemctl stop arancino
#systemctl stop redis-volatile
#systemctl stop redis-persistent

#disable services
systemctl disable arancino
#systemctl disable redis-volatile
#systemctl disable redis-persistent
echo -------------------------------------------------

echo -----Override New Environment Vars File----------
# first create arancino path
#mkdir -p "/ect/arancino"

# put the new environment file
#cp extras/vars.env /ect/arancino/vars.env

source extras/vars.env
mkdir -p $ARANCINO
mkdir -p $ARANCINOLOG
mkdir -p $ARANCINOCONF
cp extras/vars.env $ARANCINO/vars.env

echo -------------------------------------------------


#echo ---------------Unsetting env vars----------------
# unset envinronment vars
#unset ARANCINO
#unset ARANCINOCONF
#unset ARANCINOLOG
#unset ARANCINOENV
#unset FLASK_ENV
#echo -------------------------------------------------