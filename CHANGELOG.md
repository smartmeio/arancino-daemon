# Changelog

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

#### v 2.0.0 2020.07.24
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
