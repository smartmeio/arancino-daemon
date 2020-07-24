# Changelog

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
