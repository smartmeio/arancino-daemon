#!/bin/bash

echo ---Stopping and disabling services and daemons---

systemctl stop arancino

systemctl disable arancino

echo -------------------------------------------------
