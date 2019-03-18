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
--extra-index-url = https://packages.smartme.io/repository/pypi-snapshot/simple
--extra-index-url = https://packages.smartme.io/repository/pypi/simple

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
~*TODO*~


## Extras

### Run arancino as _daemon_ with _systemctl_

During installation the file _arancino.services_ was copied in _/etc/arancino/extras/_. Move _/etc/arancino/extras/arancino.service_ into _systemd_ directory and then enabled the service:

```shell

$ sudo cp /etc/arancino/extras/arancino.service /etc/systemd/system/
$ systemctl enable arancino.service

```

Run `ps` to check if Arancino daemon is up and running:

```shell

$ ps aux | grep arancino

```



