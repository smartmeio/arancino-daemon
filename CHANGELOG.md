# Changelog

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