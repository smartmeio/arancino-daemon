#!/bin/bash
echo --------------------------------------
echo "Stopping and disabling services and daemons"
#stop services (first arancino then redis)
sv down arancino
#systemctl stop redis-volatile
#systemctl stop redis-persistent

#disable services
sv-disable arancino
#systemctl disable redis-volatile
#systemctl disable redis-persistent
echo --------------------------------------

echo --------------------------------------
echo "Unsetting env vars"
# unset envinronment vars
unset ARANCINO
unset ARANCINOCONF
unset ARANCINOLOG
unset ARANCINOENV
echo --------------------------------------