#!/bin/sh

yes | redis-check-aof --fix /etc/redis/cwd/appendonly.aof