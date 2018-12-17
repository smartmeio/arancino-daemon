#!/usr/bin/env python

#redis connection parameter
redis = {'host': 'localhost',
         'port': 6379,
         'dcd_resp': True,  #decode response
         'db': 0}

# allowed vid and pid to connect to
hwid = [
        'F00A:00FA'
        ,'2A03:804E'
        ,'2341:0043'
        ]

