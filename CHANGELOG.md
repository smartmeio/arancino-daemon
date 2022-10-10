# Changelog

#### v 2.6.0 2022.10.10
* Add: added heartbeat support [#1z0eqn4](https://app.clickup.com/t/1z0eqn4)
* Add: added MQTT port type [#1nfe9zr](https://app.clickup.com/t/1nfe9zr)
* Add: added BLE UART port type [#1n9pvyv](https://app.clickup.com/t/1n9pvyv)
* Add: reset arancino port OTA [#30xfcgj](https://app.clickup.com/t/30xfcgj)

#### v 2.5.1 2022.09.16
* Fix: fixed compatibilty issue when logging in python 3.5
* Fix: fixed typo in version attribute.
* Fix: fixed yaml configuration parameter.

#### v 2.5.0 2022.07.28
* Improve: Serial ports commands are read and queued, the execution is done in a separate thread. [#31egtz3](https://app.clickup.com/t/31egtz3)
* Improve: Store and Mstore commands are executed in pipeline. [#31egugq](https://app.clickup.com/t/31egugq)
* Delete: Arancino Transmitter moved to new service. [#31egqqg](https://app.clickup.com/t/31egqqg)
* Add: support for .zip firmware extension. [#1zhvp2j](https://app.clickup.com/t/1zhvp2j ) 
* Change: configuration files type to yaml. [#1q2rh0a](https://app.clickup.com/t/1q2rh0a)
* Improve: retrieve MCU family by vid and pid on discovery, for Serial Port type. [#26b2fxb](https://app.clickup.com/t/26b2fxb)  

#### v 2.4.0 2022.01.20
* Introduced Arancino Transmitter [#gn8b8f](https://app.clickup.com/t/gn8b8f)
* Changed timestamp format sent in response of `START` command. [#j1b6yc](https://app.clickup.com/t/j1b6yc)
* Introduced Redis Time Series with the `STORE`, `MSTORE` and `STORETAGS` commands. [#acuhwp](https://app.clickup.com/t/k16ge0), [#acuhwp](https://app.clickup.com/t/k16ge0)
* Introduced `SETRSVD` command used to change the status of a Reserved Key value [#jtb0ya](https://app.clickup.com/t/jtb0ya)
* Introduced the Reserved Key `___BLNK_ID___` used to start the identification process on the microcontroller: blink for 5 seconds. [#jtaq9w](https://app.clickup.com/t/jtaq9w)
* Introduced a new API endpoint to indentify a Port (if the port implements the identify process) [#jtaq9w](https://app.clickup.com/t/jtaq9w)
* Fixed a double execution of _Arancino Commands_ [#jtb6gm](https://app.clickup.com/t/jtb6gm)
* Updated `FLUSH` command; persistent datastore will no longer be flushed, only the volatile one: [kd64rw](https://app.clickup.com/t/kd64rw)
* Change the Args of the `START` command: [k1518r](https://app.clickup.com/t/k1518r)
* Introduced a new data structure used for generic attributes and a new metadata for the MCU Family: [k1518r](https://app.clickup.com/t/k1518r)
* Fix: API Set Config misses authentication. [jz5mef](https://app.clickup.com/t/jz5mef)
* Minor bug fixes and improvments.

#### v 2.3.0 2021.04.06
* Fixed arancino config files name, now binded to ARANCINOENV var. [#g97519](https://app.clickup.com/t/g97519)
* Introduced new reserved key `___MODLOGLVL___`. [#g9786m](https://app.clickup.com/t/g9786m)
* Introduced different config "host" variables for the redis instances. [#g97ayp](https://app.clickup.com/t/g97ayp)

#### v 2.2.0 2021.03.22
* Changed server, now use GUnicorn in production. [#crw02w](https://app.clickup.com/t/crw02w)
* Removed stack trace in case of Redis connection error at start. [#f53nzb](https://app.clickup.com/t/f53nzb)
* Introduced new Reserverd Key `___MODENV___` to store the environment of the running Arancino Daemon. [#fz4f66](https://app.clickup.com/t/fz4f66)
* Now use the Reserverd Key `___MODVERS___` to store the version of the running Arancino Daemon. [#fz4baj](https://app.clickup.com/t/fz4baj)
* Introduced new Cortex Command `GETRSVD` to retrieve values from Reserved Datastore. [#acujnq](https://app.clickup.com/t/acujnq)

#### v 2.1.5 2021.03.11
* Fixed: arancino.service should start just after network.target and rc.local. Mandatory for buster based systems. [#fh5fv7](https://app.clickup.com/t/fh5fv7)

#### v 2.1.4 2021.02.5
* Fixed missing env var [#crvwm8](https://app.clickup.com/t/crvwm8)
* Fixed the way SERIAL PORT data is decoded [#dk226t](https://app.clickup.com/t/dk226t)

#### v 2.1.3 2021.01.19
* Fixed log level in config file: INFO [#b0ymd9](https://app.clickup.com/t/b0ymd9)
* Fixed api change status: errors with boolean values [#c2w294](https://app.clickup.com/t/c2w294)
* Fixed a problem that does not retrieve alias from db [#bx2hyk](https://app.clickup.com/t/bx2hyk)
* Fixed api port uptime: now returns even uptime in seconds [#bz02rz](https://app.clickup.com/t/bz02rz)
* Fixed log stack trace. Logs stack trace by default in case of errors: [#cjwqxg](https://app.clickup.com/t/cjwqxg)
* Fixed setup process [#bav3y6](https://app.clickup.com/t/bav3y6)
* Fixed api get config [#cgw47y](https://app.clickup.com/t/cgw47y)

### v 2.1.2 2020.11.25
* Fixed Post Install Script [#apw16v](https://app.clickup.com/t/apw16v)

#### v 2.1.1 2020.11.29
* Fixed compatibility matrix for Serial Port #108 [#acuxb1](https://app.clickup.com/t/acuxb1)

#### v 2.1.0 2020.10.28
* Introduced a new State called "STARTED". It represents the state of the communication between a port and Aracino Module. #99
* Fixed Rest API for port configuration (Alias, Enable/Disable, Hide/Show). #95
* Introduced Rest API for get and set Arancino configuration. #94
* Introduced `MSET` and `MGET` commands. #91
* Package improvements. #101
* Each *get-like* commands (`HSET`, `HVALS`, `HKEYS`, `HGETALL`, `MGET`) now search even in persistent data store for a key(or field). #106
* Introduced *set-like* commands (`HSET_PERS`, `MSET_PERS`) to store data in persistent datastore. #106
* `START` Commands now can receive Fw Timestamp, Fw version, Fw Name and Arancino Core Version as arguments.
* Minor bug fixes and improvements. #105, #014, #102

#### v 2.0.0 - 2020.07.24
* Now Resets each microcontroller before connecting (requires `v1.1.0` Arancino Platform)
* Changed project structure to a more modular architecture. Arancino Port Type can now be easily extended.
* Improved logger formatter.
* Introduced new different port filter types used in the discovery phase.
* Introduced a new kind of Port called Test Port, used for testing purpose
* Fix `KEYS` command: now returns even persistent keys.
* Metadata are now different for each Port Type, but they have a common set of metadata. Even the Device Store changed.
* Introduces new metadatas: _creation date_, _last usage date_, _port type_, _library version_, _compatibility_
* The key `___LIBVERS_<PORT_ID>___` stored in the Data Store are now part of common set of port metadata.
* Use Redis `MULTI` and `EXEC` trough `pipeline` in *Synch* process to reduce the back-and-forth overhead between the client and server.
* Log Console Handler and Log File Handler can be enabled directly from `arancino.cfg`
* Improved Redis Connection: now Arancino continues running even Redis has been stoppped, and reconnect when connection is restored.
* Improved Redis Connection: Arancino by default makes 5 connection attemps (each one every 3 seconds) and then exit if Redis is unreachable.
* Introduced a rest server with some API like _Enable/Disable_, _Reset_, _Upload Firmware_ etc...
* Redis configuration and systemd services are now exclueded from Arancino package. They are pre-installed in Arancino OS.
* Introduced different configuration file based on `ARANCINOENV` environment variables (`PROD`, `DEV` or `TEST`)
* Introduced `S_UPTIME` status metadata to store uptime port #78.
* Introduced a more flexible way to check command (cortex) arguments number (lass than, equal, etc...).
* Fixed Flush command. Disabled by error.
* Update protocol: `START` command now send back `port id` and `timestamp`

#### v 1.2.1 - 2020.05.25
* Fix: Missing Arancino Mignon in allowed vid-pid.

#### v 1.2.0 - 2020.04.14
* Lib version stored in device stored (compatibility with `.2.0.0`).

#### v 1.1.1 - 2020.04.09
* Fix a typo in redis services which cause and error at boot on systemd file #77.

#### v 1.1.0 - 2020.04.08
* Introduced a simple VID:PID filter for Serial Port #76
* Fix missing fix-aof.sh script file #74
* Fix arancino doesn't start at reboot beacause redis is not ready #75

#### v 1.0.4 - 2020.03.19
* Fixed a bug which doesn't disable console handler. This writes to `/var/log/syslog` and `/var/log/daemon.log` and fill up the storage. #63

#### v 1.0.3 - 2020.03.16
* Fixed a bug which prevented redis-persistent to start after an uncontrolled shutdown of the board. #53

#### v 1.0.2 - 2020.03.11
* Fixed a critical bug that prevented redis-persistent to work properly. #53

#### v 1.0.1 - 2019.12.30
* Fix a bug while checks compatibility that prevent a new version library to be released without adding it in the compatibility array. Now it uses '*' while check version number.
* Fix a bug that will not update the P_NAME Status Metadata in the Device Store (Redis).

#### v 1.0.0 - 2019.12.20
* Now it standard (sync and stable) `py-serial` serial connection instead of `py-serial-asyncio`.
* Introduced the possibility of set one or more persistent keys by the user in Arancino Library with a new command: `CMD_APP_SET_PERS`.
* Restored #29 (Reserved keys are saved when FLUSH command is received).
* Fixed FLUSH command. #39
* Fixed a bug which disconnect a device when a `GenericRedisException` and `InvalidCommandException` are raised during the command parsing. #37
* Logs are reduced and Exceptions/Error are tracked in a separetend file: `arancino.error.log`. #24
* Introduced check on versions compatibility with Arancino Library running on connected devices. #11
* Pypi packet is now only for Unix not Windows. #38
* Pypi packet runs `pre-install` and `post-install` scripts to configure the module.
* Baudrates is configurable via configuration file. #42
* Redis instance type is configurable via configuration file.
* Stats about uptime and errors on a dedicate file `/var/log/arancino/arancino.stats.log`. #43
* Colored console log. #44
* Introduce arancino.cfg as configuration file

#### v 0.1.5 - 2019.07.23
* Fix Arancino Service.

#### v 0.1.4 - 2019.04.17
* Setup.py now includes extras/*
* Log info and error enhancement. #25
* Log file size incremented form 1Mb to 10Mb (rotating).
* Reserved keys are saved when FLUSH command is received. #29

#### v 0.1.3 - 2019.03.22
* Included in Extras the fixed configuration and services Redis files for Arancino OS.

#### v 0.1.2 - 2019.03.20
* Removed python interpreter from the start.py script.

#### v 0.1.1 - 2019.03.20
* Console log handler removed (only file handler by default).
* Default file log path moved to _/var/log/arancino/_ instead of _current working dir_.
* Service file _arancino.service_ moved to _<dist-packages>/arancino/extras/_.
* Fix: `After` directive in _arancino.service_. Comma separating services.
