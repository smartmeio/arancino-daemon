#!/bin/sh

until
        [ `redis-cli -p $1 ping | grep -c PONG` = 1 ];
do
        echo "Waiting 1s for Redis at port $1 to load";
        sleep 1;
done

exit 0