# Changelog

#### v 1.1.0 2020.MM.DD
* Now Resets each microcontroller before connecting (requires v 1.1.0 Arancino Platform)
* Changed project structure to a more modular architecture. Arancino Port Type can now be easily estended.
* Improved logger formatter
* Introduced new different port filter types.
* Introduced a new kind of Port called Test Port, used for testing purpose

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
