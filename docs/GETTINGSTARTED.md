## Prerequisites
* Redis: During development you could have only one instance, in Production it's recommended have two instance; 
the second one in peristent mode. From version 2.4.0 you must install the 
[Redis TimeSeries Plugin](https://oss.redislabs.com/redistimeseries/) in the first instance. 

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
Open a terminal window in Arancino OS and run the following (pasting the previous copied url)

```shell

$ sudo pip3 install https://packages.smartme.io/repository/pypi-snapshot/packages/arancino/VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT/arancino-VERS.YYYY-MM-DD-HH-MM-SS-BRANCH-COMMIT.tar.gz

```

From Arancino OS version `1.1.0`, Arancino Package Repository is included in the source list and you can simply run `pip` to install Arancino Module:

Specific version (eg. `2.1.1`): 
```shell
$ sudo pip3 install arancino==2.1.1
```

Specific test/dev version (e.g. `2.1.1-test.1`):
```shell
$ sudo pip3 install arancino==2.1.1-test.1
``` 
 
Latest stable version:
```shell
$ sudo pip3 install arancino
``` 

NOTE: 
>Consider that in the latest versions of Arancino OS dependencies are already installed so you can use `--no-dependencies` option. 



#### Install from Release Repository
To install a release package is quite more simple, just use the Release Repository Packages url:

```shell

$ sudo pip3 install arancino --extra-index-url https://packages.smartme.io/repository/pypi/simple

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
