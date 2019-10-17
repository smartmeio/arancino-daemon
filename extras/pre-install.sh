#!/bin/bash

#stop services (first arancino then redis)
systemctl stop arancino
systemctl stop redis-volatile
systemctl stop redis-persistent

#disable services
systemctl disable arancino
systemctl disable redis-volatile
systemctl disable redis-persistent
