# Arancino: serial module for Arancino Library

Receives commands from Arancino Library (uC) trough the Arancino Cortex Protocol over serial connection


## Prerequisites
* Redis
* Python 3


## Setup

Add Smartme.IO repository as pypi source. There are two repository, one for release packages and one for development (snapshot). Open your `pip.conf` and add the following lines:

```

$ sudo vi <HOME>/.config/pip/pip.conf

.....

[global]
--extra-index-url = https://packages.smartme.io/repository/pypi/simple
                    https://packages.smartme.io/repository/pypi-snapshot/simple

```

Install Arancino Module:

```shell
$ sudo pip install arancino

```

Give exec grant

```shell

$ chmod +x <PATH TO ARANCINO MODULE>/start.py

```

## Configuration

All available configuration can be set up in the _<PATH TO ARANCINO MODULE>/arancino_conf.py_ file.  


## Extras

### Run arancino as _daemon_ with _systemctl_

During installation the file _arancino.services_ was copied in _<PATH TO ARANCINO MODULE>/extras/_. Move it to into _systemd_ directory and then enabled the service:

```shell

$ sudo cp <PATH TO ARANCINO MODULE>/extras/arancino.service /etc/systemd/system/
$ systemctl enable arancino.service
$ systemctl start arancino.service

```

Run `ps` or `systemctl status` to check if Arancino daemon is up and running:

```shell

$ systemctl status arancino

```


## Compatibility with Arancino Library


|Module Version   	|       |Library Version   	|
|---	            |---	|---                |
| `0.0.1`   	    | `==`  | `0.0.1`           |
| `0.0.2`  	        | `<=`  | `0.0.2`           |
| `0.1.0`  	        | `>=`  | `0.1.0`           |
| `0.1.1`           |       |                   |