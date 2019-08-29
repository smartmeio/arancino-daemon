# Arancino: serial module for Arancino Library

Receives commands from Arancino Library (uC) trough the Arancino Cortex Protocol over serial connection


## Prerequisites
* Redis
* Python 3


## Setup

### Install only using CLI
Use directly the command line and _pip_ by specifying the repository url as argument:

```shell

$ sudo pip3 install arancino --extra-index-url https://packages.smartme.io/repository/pypi/simple

```

or

```

$ sudo pip3 install arancino --extra-index-url https://packages.smartme.io/repository/pypi-staging/simple

```

### Install by configuring PyPi source list
Add Smartme.IO repository as pypi source. There are two repositories, one for release packages and one for development (snapshot). Open your `pip.conf` and add the following lines:

```shell

$ sudo vi <HOME>/.config/pip/pip.conf

.....

[global]
--extra-index-url = https://packages.smartme.io/repository/pypi/simple
                    https://packages.smartme.io/repository/pypi-snapshot/simple

```

Install Arancino Module:

```shell
$ sudo pip3 install arancino

```


Give exec grant

```shell

$ chmod +x <PATH TO ARANCINO MODULE>/start.py

```

## Configuration

All available configurations can be setted up in the _<PATH TO ARANCINO MODULE>/arancino_conf.py_ file.


### Log Configuration
_TODO_

### Redis Configuration
In __Arancino OS__ by default there are two running instances of Redis with two databases each one. The first instance is volatile and the second one is persistent. The volatile one is used to store application data of the Arancino firmware (e.g date read by a sensor like Temperature, Humidity etc...) (first instance first database) it is called _datastore_, The Persistent one is used to store devices informations (second instance first database) and configuration data for Arancino Firmware (second instance second database) they are called _devicestore_ and _datastore_persistant_. 

The configuration are the following:

```python
### REDIS-ARANCINO CONFIGURATION --> PRODUCTION ###

#datastore
redis_dts = {'host': 'localhost',
         'port': 6379,
         'dcd_resp': True,
         'db': 0}

#devicestore
redis_dvs = {'host': 'localhost',
         'port': 6380,
         'dcd_resp': True,
         'db': 0}

#datastore persistent
redis_dts_rsvd = {'host': 'localhost',
         'port': 6380,
         'dcd_resp': True,
         'db': 1}

```

- `host`: the host which Redis is running on.
- `port`: the port which Redis is listening on.
- `dcd_resp`: boolean value, True => decode response. 
- `db`: the database number.


Usually you don't need to change Redis configuration in Production environment, but it's useful to change this if you are in Development or Test environment and you don't have a second Redis instance. Default Redis port is __6379__ with __16__ databases. To apply default Redis configuration please change all the `ports` to __6379__ (the default port) and number the `db` from __0__ to __2__:

```python
### REDIS CONFIGURATION --> DEVELOPMENT/TEST ###

#datastore
redis_dts = {'host': 'localhost',
         'port': 6379,
         'dcd_resp': True,
         'db': 0}

#devicestore
redis_dvs = {'host': 'localhost',
         'port': 6379,
         'dcd_resp': True,
         'db': 1}

#datastore persistent
redis_dts_rsvd = {'host': 'localhost',
         'port': 6379,
         'dcd_resp': True,
         'db': 2}

```


### Arancino Port Configuration
Arancino Port rappresent an abstraction of a device plugged in to Arancino Board and/or the built-in microcontroller. The following configuration is used by Arancino Module to manage a __new device__ when it's plugged to Arancino Board:

```python
port = {
    'enabled': True,
    'auto_connect': False,
    'hide': False
}
```

- `enabled`: when `True` the plugged device is immediately connected and starts the communication, when `False` it remains __plugged__ but doesn't communicate. This option is stored into the _devicestore_ and can be changed directly by `redis-cli` or similar to enable or disable the device. 
- `auto_connect`: NOT USED AT MOMENT
- `hide`: NOT USED AT MOMENT: this option only concerns the UI. it's will be used to hide one or more device from the main device UI.

### Polling Cycle
The polling cycle time determines the interval between one scan and another of new devices. If a new device is plugged it will be discovered and connected (if `enabled` is `True`) at least after the time setted in `cycle_time`. The value is expressed in seconds.



```python
#cycle interval time
cycle_time = 10
```

## Run

To run Arancino use the `start.py' script. If you don't want to run as _root_ please change the owner of log dir, and then run Arancino:

```shell

$ sudo chown -R <USER> /var/log/arancino/
$ python3 <PATH TO ARANCINO MODULE>/start.py


```

## Extras

### Arancino as System Daemon 

#### Change `ExecStart` directive

During installation the file _arancino.services_ was copied in _<PATH TO ARANCINO MODULE>/extras/_.
Move it into _systemd_ directory and change the `ExecStart` directive to execute the _start.py_ script.

```shell
$ sudo cp <PATH TO ARANCINO MODULE>/extras/arancino.service /etc/systemd/system/
$ sudo vi /etc/systemd/system/arancino.service 

...
[Service]
Type=simple
User=root
Group=root
=====> ExecStart=<PATH TO ARANCINO MODULE>/start.py <=====
Restart=on-failure
RestartSec=3
...

``` 

#### Run arancino as _daemon_ with _systemctl_

Finally enabled and start the Aracnino service:

```shell

$ systemctl enable arancino.service
$ systemctl start arancino.service

```

Run `ps` or `systemctl status` to check if Arancino daemon is up and running:

```shell

$ systemctl status arancino

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