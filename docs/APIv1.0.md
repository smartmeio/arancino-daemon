### Arancino Rest API v1.0
Arancino API runs at HTTP port 1745. The base URL is: `http://{{host}}:1475/api/v1` where `{{host}}` is a placeholder
for the ip address or hostname of your Arancino device. They were introduced in version `2.0.0` and are organized in two main categories:

- Queries
- Operations


#### Queries API:
The queries API are useful to get information about the system and the running Arancino Daemon.

##### Hello
Returns a lot of information about the device:

- API address: `/`
- API method: `GET`
- API result:
```json
{
    "arancino": {
        "arancino": {
            "env": {
                "ARANCINO": "/etc/arancino",
                "ARANCINOCONF": "/etc/arancino/config",
                "ARANCINOENV": "TEST",
                "ARANCINOLOG": "/var/log/arancino"
            },
            "ports": {
                "connected": {
                      "TEST": [
                          "TESTPORT5"
                      ],
                      "SERIAL": [
                          "1ABDF7C5504E4B53382E314AFF0C1B2D"
                      ]
                },
                "discovered":{
                      "TEST": [
                          "TESTPORT5"
                       ],
                      "SERIAL": [
                          "1ABDF7C5504E4B53382E314AFF0C1B2D"
                      ]
                }
            },
            "uptime": [
                30285.765567541122,
                "8 hours, 24 minutes, 45 seconds"
            ],
            "version": "2.0.0"
        },
        "system": {
            "network": {
                "hostname": "testprova",
                "ifaces": [
                    {
                        "addr": "127.0.0.1",
                        "iface": "lo",
                        "netmask": "255.0.0.0",
                        "peer": "127.0.0.1"
                    },
                    {
                        "addr": "192.168.1.9",
                        "broadcast": "192.168.1.255",
                        "iface": "eth0",
                        "netmask": "255.255.255.0"
                    }
                ]
            },
            "os": [
                "arancinoOS powered by Smartme.io",
                "0.0.23"
            ],
            "uptime": [
                30752.91,
                "8 hours, 32 minutes, 32 seconds"
            ]
        }
    }
}
```

##### Arancino
Returns information about Arancino:

- API address: `/arancino`
- API method: `GET`
- API result:
```json
{
    "arancino": {
        "arancino": {
            "env": {
                "ARANCINO": "/etc/arancino",
                "ARANCINOCONF": "/etc/arancino/config",
                "ARANCINOENV": "TEST",
                "ARANCINOLOG": "/var/log/arancino"
            },
            "ports": {
                "connected": {
                      "TEST": [
                          "TESTPORT5"
                      ],
                      "SERIAL": [
                          "1ABDF7C5504E4B53382E314AFF0C1B2D"
                      ]
                },
                "discovered":{
                      "TEST": [
                          "TESTPORT5"
                       ],
                      "SERIAL": [
                          "1ABDF7C5504E4B53382E314AFF0C1B2D"
                      ]
                }
            },
            "uptime": [
                30285.765567541122,
                "8 hours, 24 minutes, 45 seconds"
            ],
            "version": "2.0.0"
        }
    }    
}
```

##### Arancino Configuration
Returns all Arancino configuration or a specific one:

- API address: `/arancino`
- API method: `GET`
- API body params:
    - empty -> return all the configurations
    - json -> return the required configurations:
```json
{
    "config": [
        {
            "section": "redis",
            "option": "host"
        },
        {
            "section": "redis",
            "option": "port_volatile"
        },
        {
            "section": "general",
            "option": "cycle_time"
        }
    ]
}
```
- API result:
```json
{
    "arancino": {
        "config": {
            "general": {
                "cycle_time": "10"
            },
            "redis": {
                "host": "localhost",
                "port_volatile": "6379"
            }
        }
    }
}

```


##### System
Returns information about OS and network:

- API address: `/system`
- API method: `GET`
- API result:
```json
{
    "arancino": {
        "system": {
            "network": {
                "hostname": "testprova",
                "ifaces": [
                    {
                        "addr": "127.0.0.1",
                        "iface": "lo",
                        "netmask": "255.0.0.0",
                        "peer": "127.0.0.1"
                    },
                    {
                        "addr": "192.168.1.9",
                        "broadcast": "192.168.1.255",
                        "iface": "eth0",
                        "netmask": "255.255.255.0"
                    }
                ]
            },
            "os": [
                "arancinoOS powered by Smartme.io",
                "0.0.23"
            ],
            "uptime": [
                32299.88,
                "8 hours, 58 minutes, 19 seconds"
            ]
        }
    }
}
```

##### Ports
Return all the ports organized in *Connected* and *Discovered*

- API address: `/ports`
- API method: `GET`
- API result:
```json
{
    "arancino": {
        "arancino": {
            "ports": {
                "connected": [
                    {
                        "B_ID": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                        "B_LIB_VER": "1.1.0",
                        "B_PORT_TYPE": "SERIAL",
                        "C_ALIAS": "",
                        "C_ENABLED": true,
                        "C_HIDE_DEVICE": false,
                        "L_DEVICE": "/dev/ttyACM0",
                        "P_DESCRIPTION": "Arancino",
                        "P_HWID": "USB VID:PID=04D8:ECDA SER=1ABDF7C5504E4B53382E314AFF0C1B2D LOCATION=1-1.2:1.0",
                        "P_INTERFACE": null,
                        "P_LOCATION": "1-1.2:1.0",
                        "P_MANUFACTURER": "smartme.IO",
                        "P_NAME": "ttyACM0",
                        "P_PID": "0xECDA",
                        "P_PRODUCT": "Arancino",
                        "P_SERIALNUMBER": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                        "P_VID": "0x04D8",
                        "S_CONNECTED": true,
                        "S_CREATION_DATE": "Thu, 21 May 2020 01:17:14 GMT",
                        "S_LAST_USAGE_DATE": "Tue, 26 May 2020 10:02:25 GMT",
                        "S_PLUGGED": true,
                        "S_COMPATIBILITY": true
                    }
                ],
                "discovered": [
                    {
                        "B_DEVICE": "There",
                        "B_ID": "TESTPORT5",
                        "B_LIB_VER": "1.0.0",
                        "B_PORT_TYPE": "TEST",
                        "C_ALIAS": "TESTPORT5",
                        "C_ENABLED": false,
                        "C_HIDE_DEVICE": true,
                        "S_CONNECTED": true,
                        "S_CREATION_DATE": "Mon, 16 Mar 2020 08:44:33 GMT",
                        "S_LAST_USAGE_DATE": "Mon, 16 Mar 2020 17:41:32 GMT",
                        "S_PLUGGED": true,
                        "S_COMPATIBILITY": true
                    },
                    {
                        "B_ID": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                        "B_LIB_VER": "1.1.0",
                        "B_PORT_TYPE": "SERIAL",
                        "C_ALIAS": "",
                        "C_ENABLED": true,
                        "C_HIDE_DEVICE": false,
                        "L_DEVICE": "/dev/ttyACM0",
                        "P_DESCRIPTION": "Arancino",
                        "P_HWID": "USB VID:PID=04D8:ECDA SER=1ABDF7C5504E4B53382E314AFF0C1B2D LOCATION=1-1.2:1.0",
                        "P_INTERFACE": null,
                        "P_LOCATION": "1-1.2:1.0",
                        "P_MANUFACTURER": "smartme.IO",
                        "P_NAME": "ttyACM0",
                        "P_PID": "0xECDA",
                        "P_PRODUCT": "Arancino",
                        "P_SERIALNUMBER": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                        "P_VID": "0x04D8",
                        "S_CONNECTED": true,
                        "S_CREATION_DATE": "Thu, 21 May 2020 01:17:14 GMT",
                        "S_LAST_USAGE_DATE": "Tue, 26 May 2020 10:02:25 GMT",
                        "S_PLUGGED": true,
                        "S_COMPATIBILITY": true
                    }
                ]
            }
        }
    }
}

```

##### Connected Ports
Return all the *Connected* ports

- API address: `/connected`
- API method: `GET`
- API result:
```json
{
    "arancino": {
        "arancino": {
            "ports": {
                "connected": [
                    {
                        "B_ID": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                        "B_LIB_VER": "1.1.0",
                        "B_PORT_TYPE": "SERIAL",
                        "C_ALIAS": "",
                        "C_ENABLED": true,
                        "C_HIDE_DEVICE": false,
                        "L_DEVICE": "/dev/ttyACM0",
                        "P_DESCRIPTION": "Arancino",
                        "P_HWID": "USB VID:PID=04D8:ECDA SER=1ABDF7C5504E4B53382E314AFF0C1B2D LOCATION=1-1.2:1.0",
                        "P_INTERFACE": null,
                        "P_LOCATION": "1-1.2:1.0",
                        "P_MANUFACTURER": "smartme.IO",
                        "P_NAME": "ttyACM0",
                        "P_PID": "0xECDA",
                        "P_PRODUCT": "Arancino",
                        "P_SERIALNUMBER": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                        "P_VID": "0x04D8",
                        "S_CONNECTED": true,
                        "S_CREATION_DATE": "Thu, 21 May 2020 01:17:14 GMT",
                        "S_LAST_USAGE_DATE": "Tue, 26 May 2020 10:02:25 GMT",
                        "S_PLUGGED": true,
                        "S_COMPATIBILITY": true
                    }
                ]
            }
        }
    }
}

```

##### Port By ID
Return all the information about the port specified by `{{PORT_ID}}`

- API address: `/ports/{{PORT_ID}}`
- API method: `GET`
- API result:

```json
{
    "arancino": {
        "arancino": {
            "port": {
                "B_ID": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                "B_LIB_VER": "1.1.0",
                "B_PORT_TYPE": "SERIAL",
                "C_ALIAS": "",
                "C_ENABLED": true,
                "C_HIDE_DEVICE": false,
                "L_DEVICE": "/dev/ttyACM0",
                "P_DESCRIPTION": "Arancino",
                "P_HWID": "USB VID:PID=04D8:ECDA SER=1ABDF7C5504E4B53382E314AFF0C1B2D LOCATION=1-1.2:1.0",
                "P_INTERFACE": null,
                "P_LOCATION": "1-1.2:1.0",
                "P_MANUFACTURER": "smartme.IO",
                "P_NAME": "ttyACM0",
                "P_PID": "0xECDA",
                "P_PRODUCT": "Arancino",
                "P_SERIALNUMBER": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                "P_VID": "0x04D8",
                "S_CONNECTED": true,
                "S_CREATION_DATE": "Thu, 21 May 2020 01:17:14 GMT",
                "S_LAST_USAGE_DATE": "Tue, 26 May 2020 10:02:25 GMT",
                "S_PLUGGED": true,
                "S_COMPATIBILITY": true
            }
        }
    }
}
```

##### Discovered Ports
Return all the *Discovered* ports

- API address: `/discovered`
- API method: `GET`
- API result:
```json
{
    "arancino": {
        "arancino": {
            "ports": {
                "discovered": [
                    {
                        "B_DEVICE": "There",
                        "B_ID": "TESTPORT5",
                        "B_LIB_VER": "1.0.0",
                        "B_PORT_TYPE": "TEST",
                        "C_ALIAS": "TESTPORT5",
                        "C_ENABLED": false,
                        "C_HIDE_DEVICE": true,
                        "S_CONNECTED": true,
                        "S_CREATION_DATE": "Mon, 16 Mar 2020 08:44:33 GMT",
                        "S_LAST_USAGE_DATE": "Mon, 16 Mar 2020 17:41:32 GMT",
                        "S_PLUGGED": true,
                        "S_COMPATIBILITY": true
                    },
                    {
                        "B_ID": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                        "B_LIB_VER": "1.1.0",
                        "B_PORT_TYPE": "SERIAL",
                        "C_ALIAS": "",
                        "C_ENABLED": true,
                        "C_HIDE_DEVICE": false,
                        "L_DEVICE": "/dev/ttyACM0",
                        "P_DESCRIPTION": "Arancino",
                        "P_HWID": "USB VID:PID=04D8:ECDA SER=1ABDF7C5504E4B53382E314AFF0C1B2D LOCATION=1-1.2:1.0",
                        "P_INTERFACE": null,
                        "P_LOCATION": "1-1.2:1.0",
                        "P_MANUFACTURER": "smartme.IO",
                        "P_NAME": "ttyACM0",
                        "P_PID": "0xECDA",
                        "P_PRODUCT": "Arancino",
                        "P_SERIALNUMBER": "1ABDF7C5504E4B53382E314AFF0C1B2D",
                        "P_VID": "0x04D8",
                        "S_CONNECTED": true,
                        "S_CREATION_DATE": "Thu, 21 May 2020 01:17:14 GMT",
                        "S_LAST_USAGE_DATE": "Tue, 26 May 2020 10:02:25 GMT",
                        "S_PLUGGED": true,
                        "S_COMPATIBILITY": true
                    }
                ]
            }
        }
    }
}

```

#### Operations API:
Those API are accesbile with authentication becouse they have impact in the running Arancino Daemon. To access them \
you can use every user defined in Arancino OS except `root`, ie: use the user `me`.


##### Set Arancino Configuration
Set a generic configuration specified by `section` and `option` of the configuration file.

- API address: `/arancino/config`
- API method: `POST`
- API query param: 
    - `section`: the section name of the configuration file
    - `option`: the option name of the section in the configuration file
    - `value`: the value of the specified option

- API header param: `Content-Type` : `application/x-www-form-urlencoded`
- API result if configuration succeed: 
```json
{
    "arancino": {
        "response": [
            {
                "internalMessage": [
                    "Arancino configured successfully"
                ],
                "isError": false,
                "returnCode": 18,
                "userMessage": "Arancino configured successfully"
            }
        ]
    }
}

```

- API result if you missed a parameter (`section` in the example below):
```json
{
    "arancino": {
        "response": [
            {
                "internalMessage": [
                    null,
                    "Configuration Section is empty"
                ],
                "isError": true,
                "returnCode": 26,
                "userMessage": "Sorry, no section configuration found during this operation"
            }
        ]
    }
}
```



##### Port Enable
Enables the port specified by `{{PORT_ID}}`


- API address: `/ports/{{PORT_ID}}/enable`
- API method: `POST`
- API result if Enable success:
```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Port enabled successfully."],
                "returnCode": 2,
                "userMessage": "Port enabled successfully."
            }
        ]
    }
}

```

- API result if port is already enabled:
```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Selected port is already enabled."],
                "returnCode": 1,
                "userMessage": "Selected port is already enabled."
            }
        ]
    }
}
```


##### Port Disable
Disables the port specified by `{{PORT_ID}}`

- API address: `/ports/{{PORT_ID}}/disable`
- API method: `POST`
- API result if Disable success:

```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Port disabled successfully."],
                "returnCode": 3,
                "userMessage": "Port disabled successfully."
            }
        ]
    }
}
```
- API result if port is already disabled:
```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Selected port is already disabled."],
                "returnCode": 4,
                "userMessage": "Selected port is already disabled."
            }
        ]
    }
}
```

##### Port Hide
Flag port specified by `{{PORT_ID}}` as _hidden_

- API address: `/ports/{{PORT_ID}}/hide`
- API method: `POST`
- API result if Hide success:

```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Port hidden successfully"],
                "returnCode": 14,
                "userMessage": "Port hidden successfully."
            }
        ]
    }
}
```
- API result if port is already hidden:

```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Selected port is already hidden"],
                "returnCode": 13,
                "userMessage": "Selected port is already hidden"
            }
        ]
    }
}
```


##### Port Show
Flag port specified by `{{PORT_ID}}` as _not hidden_

- API address: `/ports/{{PORT_ID}}/show`
- API method: `POST`
- API result if Show success:

```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Port shown successfully"],
                "returnCode": 16,
                "userMessage": "Port shown successfully."
            }
        ]
    }
}
```
- API result if port is already shown:

```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Selected port is already shown"],
                "returnCode": 15,
                "userMessage": "SSelected port is already shown"
            }
        ]
    }
}
```


##### Port Config
Used to set up generic port configuration. It allow to send configuration parameters in to the  body request.

- API address: `/ports/{{PORT_ID}}/config`
- API method: `POST`
- API body param: 
    - `enabled`: `true`/`false`
    - `hidden`: `true`/`false`
    - `alias`: `your prefered name for the port in string format`
- API result if Config success:

```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Port configured successfully"],
                "returnCode": 17,
                "userMessage": "Port configured successfully"
            }
        ]
    }
}
```

##### Reset
Send a reset command to port specified by `{{PORT_ID}}`

- API address: `/ports/{{PORT_ID}}/reset`
- API method: `POST`
- API result if Reset success:
```json
{
    "arancino": {
        "messages": [
            {
                "internalMessage": ["Port reset successfully "],
                "returnCode": 9,
                "userMessage": "Port reset successfully."
            }
        ]
    }
}

```
- API result if Reset is not implemented for the port:
```json
{
    "arancino": {
        "errors": [
            {
                "internalMessage": ["This port does not provide reset operation"],
                "returnCode": 10,
                "userMessage": "This port does not provide reset operation"
            }
        ]
    }
}
```


##### Upload
Uploads firmware to the port specified by `{{PORT_ID}}`

- API address: `/ports/{{PORT_ID}}/upload`
- API method: `POST`
- API body param: `firmware`: `the file of the firmware`
- API header param: `Content-Type` : `application/x-www-form-urlencoded`
- API result if Upload success: # TODO
- API result if Upload is not implemented for the port:
```json
{
    "arancino": {
        "errors": [
            {
                "internalMessage": ["This port does not provide upload operation"],
                "returnCode": 12,
                "userMessage": "This port does not provide upload operation"
            }
        ]
    }
}
```


#### Common result for not found port:

```json
{
    "arancino": {
        "errors": [
            {
                "internalMessage": ["Sorry, can not find specified port. Probably port was disconnected or unplugged during this operation."],
                "returnCode": 20,
                "userMessage": "Sorry, can not find specified port. Probably port was disconnected or unplugged during this operation."
            }
        ]
    }
}
```

##### API Return Codes for Operations:

| Val   | Code  |
|---    |---    |
|OK_ALREADY_ENABLED | 1 |
|OK_ENABLED | 2 |
|_________________________________________|____|
|OK_ALREADY_DISABLED | 3 |
|OK_DISABLED | 4 |
|_________________________________________|____|
|OK_ALREADY_CONNECTED | 5 |
|OK_CONNECTED | 6|
|_________________________________________|____|
|OK_ALREADY_DISCONNECTED | 7|
|OK_DISCONNECTED | 8|
|_________________________________________|____|
|OK_RESET | 9|
|OK_RESET_NOT_PROVIDED | 10|
|_________________________________________|____|
|OK_UPLOAD | 11|
|OK_UPLOAD_NOT_PROVIDED | 12|
|_________________________________________|____|
|OK_ALREADY_HIDDEN | 13|
|OK_HIDDEN | 14|
|_________________________________________|____|
|OK_ALREADY_SHOWN | 15|
|OK_SHOWN | 16|
|_________________________________________|____|
|OK_CONFIGURED | 17|
|_________________________________________|____|
|ERR_PORT_NOT_FOUND | 20|
|ERR_CAN_NOT_CONNECT_PORT_DISABLED | 21|
|ERR_GENERIC | 22|
|ERR_RESET | 23|
|ERR_UPLOAD | 24|
