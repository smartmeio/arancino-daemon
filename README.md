# Arancino: Module for Arancino Cortex Protocol

It's designed to run on Arancino OS, but can run on Unix-based systems. It manages serial connections by default and can be extended to other communication channel. Each connection must
implement the Arancino Cortex Protocol. It can manage multiple connection at time.

## Prerequisites
* Redis
* Python 3


## Setup


> Note: if you previously installed one of the previous versions (1. *. *) it is recommended that you flush the
>redis databases. Many keys have different names and others have been eliminated.


### Install Arancino Module using CLI
There are two repositories, one for release packages and one for development (snapshot), both are available in [packages.smartme.io](https://packages.smartme.io).

NOTE:
> In the latest versions of Arancino OS file system is in Read Only mode, turn it in Read Write mode with the following command:
>
> ```shell
> $ rootrw
> ```


#### Install from Development Repository
To install a develpment version of the Arancino Module please go to smartme.io [packages repository](https://packages.smartme.io)
and then browse [pypi-snapshot/arancino](https://packages.smartme.io/#browse/browse:pypi-snapshot) to your desiderd package.
Select the _tar.gz_ file and finally from the _Summary_ tab find the _Path_ field and copy the package url.
It looks like this: https://packages.smartme.io/repository/pypi-snapshot/packages/arancino/VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT/arancino-VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT.tar.gz.
Open a terminal window in Arancino OS and run the following (pasting the preovious copied url)

```shell

$ sudo pip3 install https://packages.smartme.io/repository/pypi-snapshot/packages/arancino/VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT/arancino-VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT.tar.gz

```

#### Install from Release Repository
To install a release package is quite more simple, just use the Release Repository Packages url:

```shell

$ sudo pip3 install arancino --extra-index-url https://packages.smartme.io/repository/pypi/simple

```

## Configuration

All available configurations can be setted up in the configuration file: `/etc/arancino/config/arancino.cfg`.


### Log Configuration
Arancino Module uses python logging system and writes logs to three files in `/var/log/arancino/`. To manage logs go to `[log]` section of the configuration file.

#### Log Files
You can change the logs file name changing the following properties

```ini
log = arancino.log
error = arancino.error.log
```

#### Log Level
Log level is `INFO` by default. All available levels are:

- ERROR
- WARNING
- INFO
- DEBUG

and can be changed in the following property:

```ini
level = INFO
```

#### Handlers
At the moment only two log handlers are available in arancino:

- Console
- File

Sometimes could be useful to have logs in the console instead of file, for example during development or test. By default console is disabled in production.

```ini
handler_console = False
handler_file = True
```
Only for the File handler are available the following options

Size in MBytes only for file handler. Min: 1, Max: 5, Default: 1
```ini
size = 1
```

By default File handler works in rotation mode. You can specify the number of files to use in rotate mode. Min: 1, Max: 10, Default: 1
```ini
rotate = 1
```

You can specify the file name of log files. There are two different and the error one is used to log only errors.
```ini
file_log = arancino.log
file_error = arancino.error.log
```


### Redis Configuration

>In __Arancino OS__ by default there are two running instances of Redis with six databases each one.
>The first instance is volatile and the second one is persistent.
>The volatile one is used to store application data of the Arancino firmware (e.g date read by a sensor like Temperature, Humidity etc...) (first instance first database)
>it is called _datastore_, The Persistent one is used to store devices informations (second instance first database) and configuration data for Arancino Firmware (second instance second database) they are called _devicestore_ and _datastore_persistant_.

Usually you don't need to change Redis configuration in Production environment, but it's useful to change this if you are
in Development or Test environment and you don't have a second Redis instance. The default (Production) configuration
in Arancino OS are the following:


|Parameters         |Data Store         |Device Store       |Persistent Device Store        |
|-------------------|-------------------|-------------------|-------------------------------|
|Host               |localhost          |localhost          |localhost                      |
|Port               |6379               |6380               |6380                           |
|Decode Response    |True               |True               |True                           |
|Database Number    |0                  |0                  |1                              |

During development we assume that is only one Redis instance running in volatile mode, and the configuration is:

|Parameters         |Data Store         |Device Store       |Persistent Device Store        |
|-------------------|-------------------|-------------------|-------------------------------|
|Host               |localhost          |localhost          |localhost                      |
|Port               |6379               |6379               |6379                           |
|Decode Response    |True               |True               |True                           |
|Database Number    |0                  |1                  |2                              |

Port, host and others are configured inside the `/etc/arancino/config/arancino.cfg`, in the Redis section

```ini
# redis server host
host = localhost

# redis server port of volatile instance
port_volatile = 6379

# redis server port of persistent instance
port_persistent = 6380

# decode response in redis connectetion
decode_response = True

# policy for data storage: accetpted values are: VOLATILE, PERSISTENT, VOLATILE_PERSISTENT
# VOLATILE:
instance_type = VOLATILE

# redis connection attempts: -1 -> no limits, default 5 (every 3 seconds)
connection_attempts = 5
```

The database to use in each configuration are setted in the specific section: `redis.volatile`, `redis.persistent` and `redis.volatile_persistent`:

```ini
[redis.volatile]

datastore_std_db = 0
datastore_dev_db = 1
datastore_per_db = 2

[redis.persistent]

datastore_std_db = 0
datastore_dev_db = 1
datastore_per_db = 2

[redis.volatile_persistent]

datastore_std_db = 0
datastore_dev_db = 0
datastore_per_db = 1
```

[//]: # (### Environment)

[//]: # (If you want to switch from `prod` to `dev` configuration, and viceversa open _arancino.cfg_ and change `env` property in `[general]` section:)

[//]: # (```ini)
[//]: # (# Environment type: DEV, PROD. DEV automatically sets: redis.instance_type = VOLATILE, )
[//]: # (# log.level = DEBUG, general.cycle_time = 5 and enables the console handlers)
[//]: # (env = PROD)
[//]: # (```)

### Polling Cycle
The polling cycle time determines the interval between one scan and another of new devices. If a new device is plugged
it will be discovered and connected (if `enabled` is `True` in [Arancino Ports](#arancino-ports) configuration) at least
after the time setted in `cycle_time`. The value is expressed in seconds. To change this time, change `cycle_time` property in `[general]` section.

```ini
#cycle interval time
cycle_time = 10
```

### Arancino Ports
Arancino Module scans serial ports for new devices to connect to. If a new device is plugged Arancino Module applies
the configuration of the `[port]` section of the configuration file. From version `2.0.0` Arancino module supports
multiple port types, and configurations are now specific for each type in a dedicated section of configuration file.


> News in `2.0.0`:
>
> Filters: each port type could have a filter used in the discovery phase to filter discovered ports. ie: in Serial Port Type
> the filter is based on VID and PID of serial devices. In general, there are three kind of filters: ALL (filter is disabled),
> EXCLUDE (excludes every _port_ specified in the list) and ONLY (accepts only the _port_ specified_ in the list ).
>
> Upload: With the introduction of Rest API in arancino module, it's possible to upload a firmware to a specified Port.
> The Upload command is defined in the section of the port kind. The `upload_command` can accepts placeholder in order to compose
> a real command to be spawn as sub process. Placeholder are the attributes of the class `Port` and its subclasses
> (every subclass represent a kind of port ) and must be passed between `{{` and `}}`
>
> For each Port Type:
>
> | Value       | Placeholder |
> |-------------|-------------|
> | Id          | `port._id`  |
> | Device      | `port._device`|
> | Port Type   | `port._port_type`|
> | Port Type   | `port._port_type`|
> | Library Version | `port._library_version` |
> | Creation Date | `port._m_b_creation_date` |
> | Last Usage Date | `port._m_b_last_usage_date` |
> | Is Plugged ? | `port._m_s_plugged` |
> | Is Connected | `port._m_s_connected` |
> | is Enabled | `port._m_c_enabled` |
> | Alias| `port._m_c_alias` |
> | Is Hidden | `port._m_c_hide` |
> |-------------|-------------|
>
>
> Specific for Serial Port Type:
>
> | Value       | Placeholder |
> |------------|-------------|
> | Communication Baudrate | `port.__comm_baudrate` |
> | Reset Baudrate| `port.__reset_baudrate` |
> | Timeout | `port.__timeout` |
> | VID | `port.__m_p_vid` |
> | PID| `port.__m_p_pid` |
> | Name | `port.__m_p_name` |
> | Description | `port.__m_p_description` |
> | Hardware Id | `port.__m_p_name` |
> | Port Name | `port.__m_p_hwid` |
> | Serial Number | `port.__m_p_serial_number` |
> | Location | `port.__m_p_location` |
> | Manufacturer | `port.__m_p_manufacturer` |
> | Product | `port.__m_p_product` |
> | Interface | `port.__m_p_interface` |
>
> The only one placeholder that is not an attribute of the Port classes i `firmware` which represent the filename absolute
> path of the firmware to be uploaded
>
> | Value       | Placeholder |
> |------------|-------------|
> | Firmware | `firmware` |



#### Arancino Serial Ports

Configuration Section for Serial Port Type:

```ini
# default 'arancino port' configuration status
[port.serial]

# automatically connect a new discovered device
enabled = True

# set to true to make it not visible in the main device view in the UI
hide = False

# baudrate used for 'touch' reset
reset_baudrate = 300

# Filter works with the below list of VID:PID. Accepted filter type are: EXCLUDE, ONLY, ALL
# EXCLUDE: excludes the ones in the list.
# ONLY: acceptes only the ones in the list.
# ALL: no filter, accepts all. This is the default filter type.
filter_type=ALL

# List of VID:PID used to make a filter
filter_list = ["0x04d8:0xecd9", "0x04d8:0xecd9","0x04d8:0xecd9"]

# The command to run to do a firmware upload
upload_command = /usr/bin/run-bossac-cli {port._device} {firmware}
```

#### Arancino Test Ports
This is new in version `2.0.0` and it's used to make tests of Cortex commands, stress test or unit test:

```ini
[port.test]
# automatically enable (and connect) a new discovered port
enabled = True

# set to true to make it not visible in the main device view in the UI
hide = True

# Filter works with the below list of VID:PID. Accepted filter type are: EXCLUDE, ONLY, ALL
# EXCLUDE: excledus the ones in the list.
# ONLY: acceptes only the ones in the list.
# ALL: no filter, accepts all. This is the default filter type.
filter_type=ALL

# List of VID:PID used to make a filter
filter_list = []

# the number of port to create for test purpose
num = 0

# delay between each command in seconds (accept float). Default 500ms

delay = 0.5

# prefix of the id generated for the test port
id_template = TESTPORT

# command to be spawn when upload api is called. The command could have one or more placeholders.
upload_command =
```


### Environmental Variables
Arancino Module sets up 4 environmental variables during installation. Some of they referes to Arancino OS file system. These variables are setted up by systemd arancino service:

```ini
ARANCINO=/etc/arancino
ARANCINOCONF=/etc/arancino/config
ARANCINOLOG=/var/log/arancino
ARANCINOENV=PROD
```

To run locally Arancino Module please set up the same variables and change the values based on your environment

#### Visual Studio Code
Following a _configuration_ for `launch.json` of Visual Studio Code

```json
{
    "configurations": [
        {
            "name": "Arancino Run",
            "type": "python",
            "request": "launch",
            "env": {
                "ARANCINO": "${cwd}",
                "ARANCINOCONF": "${cwd}/config",
                "ARANCINOLOG": "${cwd}/log",
                "ARANCINOENV": "DEV"
            },
            "program": "${cwd}/start.sh",
            "console": "integratedTerminal"
        }
    ]
}
```

#### PyCharm
Please go to _Run_ -> _Edit Configurations_. In the new configuration setup, please ad the following line into
the _Environment_ -> _Environment Variables_ field:

```
ARANCINO=/Users/sergio/Source/git.smartme.io/arancino/arancino-module;ARANCINOCONF=/Users/sergio/Source/git.smartme.io/arancino/arancino-module/config;ARANCINOLOG=/Users/sergio/Source/git.smartme.io/arancino/arancino-module/log;ARANCINOENV=DEV;FLASK_ENV=development
```

## Extras

### Arancino as System Daemon in Arancino OS

During installation a systemd service for Arancino will be set up. The Arancino service, as explained above, will set up some environment variables. These are visibile only to Arancino. To start Arancino, systemd make a call to `/usr/local/bin/arancino/` which is the binary distributed during installation.

**Note**
> Please don't run directly `arancino` from the terminal
> ```shell
> $ aracino
> ```
> This will doesn't work because making a direct call will not set environmental variables.

The pypi installation will finally enable and start the Aracnino service. You can run `ps` or `systemctl status` to check if Arancino daemon is up and running:

```shell

$ systemctl status arancino

● arancino.service - Arancino
   Loaded: loaded (/etc/systemd/system/arancino.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2019-11-19 11:23:18 UTC; 33min ago
 Main PID: 31125 (arancino)
   CGroup: /system.slice/arancino.service
           └─31125 /usr/bin/python3 /usr/local/bin/arancino

```

#### Start Arancino

```shell
$ sudo systemctl start arancino
```

#### Stop Arancino

```shell
$ sudo systemctl stop arancino
```


### Arancino Rest API v1.0
Arancino API runs at HTTP port 1745. The base URL is: `http://{{host}}:1475/api/v1.0` where `{{host}}` is a placeholder
for the ip address or hostname of your Arancino device. They were introduced in version `2.0.0` and are organized in two main categories:

- Queries
- Operations


#### Queries API:
The queries API are useful to get information about the system and the running Arancino Module.

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
Those API are accesbile with authentication becouse they have impact in the running Arancino Module. To access them \
you can use every user defined in Arancino OS except `root`, ie: use the user `me`.





##### Enable
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


##### Disable
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

##### Hide
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


##### Show
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


##### Config
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


## Compatibility Matrix

### Compatibility with Arancino Library (for Arancino Serial Port on samd21 microcontrollers)

|Module Version   	|       |Library Version   	|
|---				        |---	  |---				        |
| `0.0.1`			| `==`	| `0.0.1`			|
| `0.0.2`			| `<=`	| `0.0.2`			|
| `0.1.0`			| `>=`	| `0.1.0`			|
| `0.1.1`			|		|					|
| `0.1.2`			|		|					|
| `0.1.3`			|		|					|
| `0.1.4`			|		|					|
| `0.1.5`			|		|					|
| `1.0.0`			| `>=`	| `1.0.0`			|
| `1.0.1`			| `>=`	| `1.0.0-rc`	|
| 					  | `<=`	| `1.*.*`			|
| `1.0.2`			| `>=`	|					|
| `1.0.3`			| `>=`	|					|
| `1.0.4`			| `=`	| `0.2.0`			|
| `1.1.0`			| `=`	|					|
| `1.1.1`			| `=`	|					|
| `1.2.0`			| `=`	|					|
| `1.2.1`			| `=`	|					|
| `2.0.0`			| `>=`	| `0.3.0`			|
|					    |		    |					    |

### Compatibility with Test Port

|Module Version   	|       |Library Version   	|
|---	              |---	  |---                |
| `2.0.0`			| `>=`	| `1.1.0`			|
|					    |		    |   					|
