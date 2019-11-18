# Arancino: serial module for Arancino Library

Receives commands from Arancino Library (uC) trough the Arancino Cortex Protocol over serial connection. It's designed to run under Arancino OS and can manage multiple serial connections.


## Prerequisites
* Redis
* Python 3


## Setup

### Install Arancino Module using CLI
There are two repositories, one for release packages and one for development (snapshot), both are available in [packages.smartme.io](https://packages.smartme.io).

#### Install from Development Repository
To install a develpment version of the Arancino Module please go to smartme.io [packages repository](https://packages.smartme.io) and then browse [pypi-snapshot/arancino](https://packages.smartme.io/#browse/browse:pypi-snapshot) to your desiderd package. Select the _tar.gz_ file and finally from the _Summary_ tab find the _Path_ field and copy the package url. It looks like this: https://packages.smartme.io/repository/pypi-snapshot/packages/arancino/VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT/arancino-VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT.tar.gz.
Open a terminal window in Arancino OS and run the following (pasting the preovious copied url)

```shell

$ sudo pip3 install https://packages.smartme.io/repository/pypi-snapshot/packages/arancino/VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT/arancino-VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT.tar.gz

```

#### Install from Release Repository
To install a release package is quite more simple, just use the Release Repository Packages url:

```shell

$ sudo pip3 install arancino --extra-index-url https://packages.smartme.io/repository/pypi/simple

```

NOTE:
> In the latest versions of Arancino OS file system is in Read Only mode, turn it in Read Write mode with the following command:
> 
> ```shell
> $ rootrw
> ```


Give exec grant

```shell

$ chmod +x <PATH TO ARANCINO MODULE>/start.py

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
stats = arancino.stats.log
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

#### Console
Sometimes could be useful to have logs in the console during development or test. By default console is disabled in production, and can be enabled changing the following property:
```ini
console = False
```

### Redis Configuration

> In __Arancino OS__ by default there are two running instances of Redis with two databases each one. The first instance is volatile and the second one is persistent. The volatile one is used to store application data of the Arancino firmware (e.g date read by a sensor like Temperature, Humidity etc...) (first instance first database) it is called _datastore_, The Persistent one is used to store devices informations (second instance first database) and configuration data for Arancino Firmware (second instance second database) they are called _devicestore_ and _datastore_persistant_. 


Port, host and others are configured inside the _arancino_conf.py_. 

Usually you don't need to change Redis configuration in Production environment, but it's useful to change this if you are in Development or Test environment and you don't have a second Redis instance. The default (Production) configuration in Arancino OS are the following:


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



[//]: # (### Environment)

[//]: # (If you want to switch from `prod` to `dev` configuration, and viceversa open _arancino.cfg_ and change `env` property in `[general]` section:)

[//]: # (```ini)
[//]: # (# Environment type: DEV, PROD. DEV automatically sets: redis.instance_type = VOLATILE, )
[//]: # (# log.level = DEBUG, general.cycle_time = 5 and enables the console handlers)
[//]: # (env = PROD)
[//]: # (```)

### Polling Cycle
The polling cycle time determines the interval between one scan and another of new devices. If a new device is plugged it will be discovered and connected (if `enabled` is `True` in [Arancino Ports](#arancino-ports) configuration) at least after the time setted in `cycle_time`. The value is expressed in seconds. To change this time, change `cycle_time` property in `[general]` section.

```ini
#cycle interval time
cycle_time = 10
```

### Arancino Ports
Arancino Module scans serial ports for new devices to connect to. If a new device is plugged Arancino Module applies the configuration of the `[port]` section of the configuration file.

```ini
# default 'arancino port' configuration status
[port]

# automatically connect a new discovered device
enabled = True

# NOT USED
auto_connect = False

# set to true to make it not visible in the main device view in the UI
hide = False

# default baudarate
baudrate = 4000000
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

    "configurations": [
        {
            "name": "Arancino Run",
            "type": "python",
            "request": "launch",
            "env": {
                "ARANCINO": "${cwd}",
                "ARANCINOCONF": "${cwd}/config",
                "ARANCINOLOG": "${cwd}/log",
                "ARANCINOENV": "DEV",
            },
            "program": "${cwd}/arancino/start.py",
            "console": "integratedTerminal",
        }
    ]
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

### Redis daemons configuration
_TODO_
 


## Compatibility with Arancino Library


|Module Version   	|       |Library Version   	|
|---	            |---	|---                |
| `0.0.1`   	    | `==`  | `0.0.1`           |
| `0.0.2`  	        | `<=`  | `0.0.2`           |
| `0.1.0`  	        | `>=`  | `0.1.0`           |
| `0.1.1`           |       |                   |
| `0.1.2`           |       |                   |
| `0.1.3`           |       |                   |
| `0.1.4`           |       |                   |
| `0.1.5`           |       |                   |
| `1.0.0`           | `>=`  | `1.0.0`           |
|                   |       |                   |