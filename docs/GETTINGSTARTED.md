## Prerequisites
* Redis
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
Open a terminal window in Arancino OS and run the following:

Specific version (eg. `2.1.1`): 
```shell
$ pip3 install --no-cache-dir --no-dependencies arancino==2.1.1
```

Specific test/dev version (e.g. `2.1.1-test.1`):
```shell
$ pip3 install --no-cache-dir --no-dependencies arancino==2.1.1-test.1
``` 
 
Latest stable version:
```shell
$ pip3 install --no-cache-dir --no-dependencies arancino
``` 

Please note that in Arancino OS releases earlier than `1.1.0`, the Arancino Package Repository is not included as default entry in the extra-index-url list. So, for this reason, you have to manually create or edit the general purpose `/etc/pip.conf` settings file and add the following section to it:

```
[global]
extra-index-url= https://packages.smartme.io/repository/pypi/simple
                 https://packages.smartme.io/repository/pypi-snapshot/simple
```

after that, please follow the steps listed above to install the module.

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
> $ arancino
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
