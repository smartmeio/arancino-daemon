
## Configuration

All available configurations can be setted up in the configuration file: `/etc/arancino/config/arancino.cfg`.


### Log Configuration
Arancino Daemon uses python logging system and writes logs to three files in `/var/log/arancino/`. To manage logs go to `[log]` section of the configuration file.

#### Log Files
You can change the logs file name changing the following properties

```ini
log = arancino.log
error = arancino.error.log
```

#### Log Level
Log level is `INFO` by default. All available levels are:

- ERROR
- WARNING
- INFO
- DEBUG

and can be changed in the following property:

```ini
level = INFO
```

#### Handlers
At the moment only two log handlers are available in arancino:

- Console
- File

Sometimes could be useful to have logs in the console instead of file, for example during development or test. By default console is disabled in production.

```ini
handler_console = False
handler_file = True
```
Only for the File handler are available the following options

Size in MBytes only for file handler. Min: 1, Max: 5, Default: 1
```ini
size = 1
```

By default File handler works in rotation mode. You can specify the number of files to use in rotate mode. Min: 1, Max: 10, Default: 1
```ini
rotate = 1
```

You can specify the file name of log files. There are two different and the error one is used to log only errors.
```ini
file_log = arancino.log
file_error = arancino.error.log
```


### Redis Configuration

>In __Arancino OS__ by default there are two running instances of Redis with six databases each one.
>The first instance is volatile and the second one is persistent.
>The volatile one is used to store application data of the Arancino firmware (e.g date read by a sensor like Temperature, Humidity etc...)
>it is called _Datastore_, The Persistent one is used to store devices informations and configuration 
>data for the Arancino Firmwares, they are called _Devicestore_ and _Persistent Datastore_. 
>From version `2.4.0` were introduced two new databases in the volatile instances: _Reserved Datastore_ used to manage working data and configurations,
>and _Time Series Store_ that introduced a new data type used to store Time Series data in Redis. 
>From version `2.4.0` was also introduced a new database in the persistent instance: _Tag Store_ used to manage the tags of timeseries data.

Usually you don't need to change Redis configuration in Production environment, but it's useful to change this if you are
in Development or Test environment and you don't have a second Redis instance. The default (Production) configuration
in Arancino OS are the following:


|Parameters         |Data Store         |Device Store       |Persistent Data Store  |Reserved Data Store   |Time Series Store   |Tag Store           |
|-------------------|-------------------|-------------------|-----------------------|----------------------|--------------------|--------------------|
|Host               |localhost          |localhost          |localhost              |localhost             |localhost           |localhost           |
|Port               |6379               |6380               |6380                   |6379                  |6379                |6380                |
|Decode Response    |True               |True               |True                   |True                  |True                |True                |
|Database Number    |0                  |0                  |1                      |1                     |2                   |2                   |


During development we assume that is only one Redis instance running in volatile mode, and the configuration is:

|Parameters         |Data Store         |Device Store       |Persistent Device Store  |Reserved Data Store   |Time Series Store   |Tag Store          |
|-------------------|-------------------|-------------------|-------------------------|----------------------|--------------------|-------------------|
|Host               |localhost          |localhost          |localhost                |localhost             |localhost           |localhost          |
|Port               |6379               |6379               |6379                     |6379                  |6379                |6379               |
|Decode Response    |True               |True               |True                     |True                  |True                |True               |
|Database Number    |0                  |1                  |2                        |3                     |4                   |5                  |


Port, host and others are configured inside the `/etc/arancino/config/arancino.cfg`, in the Redis section

```ini
# redis server host
host = localhost

# redis server port of volatile instance
port_volatile = 6379

# redis server port of persistent instance
port_persistent = 6380

# decode response in redis connectetion
decode_response = True

# policy for data storage: accetpted values are: VOLATILE, PERSISTENT, VOLATILE_PERSISTENT
# VOLATILE:
instance_type = VOLATILE

# redis connection attempts: -1 -> no limits, default 5 (every 3 seconds)
connection_attempts = 5
```

The database to use in each configuration are setted in the specific section: `redis.volatile`, `redis.persistent` and `redis.volatile_persistent`:

```ini
[redis.volatile]

datastore_std_db = 0
datastore_dev_db = 1
datastore_per_db = 2
datastore_rsvd_db = 3
datastore_tse_db = 4
datastore_tag_db = 5

[redis.persistent]

datastore_std_db = 0
datastore_dev_db = 1
datastore_per_db = 2
datastore_rsvd_db = 3
datastore_tse_db = 4
datastore_tag_db = 5


[redis.volatile_persistent]

datastore_std_db = 0
datastore_rsvd_db = 1
datastore_tse_db = 2

datastore_dev_db = 0
datastore_per_db = 1
datastore_tag_db = 2

### Polling Cycle
The polling cycle time determines the interval between one scan and another of new devices. If a new device is plugged
it will be discovered and connected (if `enabled` is `True` in [Arancino Ports](#arancino-ports) configuration) at least
after the time setted in `cycle_time`. The value is expressed in seconds. To change this time, change `cycle_time` property in `[general]` section.

```ini
#cycle interval time
cycle_time = 10
```

### Arancino Ports
Arancino Daemon scans serial ports for new devices to connect to. If a new device is plugged Arancino Daemon applies
the configuration of the `[port]` section of the configuration file. From version `2.0.0` Arancino Daemon supports
multiple port types, and configurations are now specific for each type in a dedicated section of configuration file.


> News in `2.0.0`:
>
> Filters: each port type could have a filter used in the discovery phase to filter discovered ports. ie: in Serial Port Type
> the filter is based on VID and PID of serial devices. In general, there are three kind of filters: ALL (filter is disabled),
> EXCLUDE (excludes every _port_ specified in the list) and ONLY (accepts only the _port_ specified_ in the list ).
>
> Upload: With the introduction of Rest API in Arancino Daemon, it's possible to upload a firmware to a specified Port.
> The Upload command is defined in the section of the port kind. The `upload_command` can accepts placeholder in order to compose
> a real command to be spawn as sub process. Placeholder are the attributes of the class `Port` and its subclasses
> (every subclass represent a kind of port ) and must be passed between `{{` and `}}`
>
> For each Port Type:
>
> | Value       | Placeholder |
> |-------------|-------------|
> | Id          | `port._id`  |
> | Device      | `port._device`|
> | Port Type   | `port._port_type`|
> | Port Type   | `port._port_type`|
> | Library Version | `port._library_version` |
> | Creation Date | `port._m_b_creation_date` |
> | Last Usage Date | `port._m_b_last_usage_date` |
> | Is Plugged ? | `port._m_s_plugged` |
> | Is Connected | `port._m_s_connected` |
> | is Enabled | `port._m_c_enabled` |
> | Alias| `port._m_c_alias` |
> | Is Hidden | `port._m_c_hide` |
> |-------------|-------------|
>
>
> Specific for Serial Port Type:
>
> | Value       | Placeholder |
> |------------|-------------|
> | Communication Baudrate | `port.__comm_baudrate` |
> | Reset Baudrate| `port.__reset_baudrate` |
> | Timeout | `port.__timeout` |
> | VID | `port.__m_p_vid` |
> | PID| `port.__m_p_pid` |
> | Name | `port.__m_p_name` |
> | Description | `port.__m_p_description` |
> | Hardware Id | `port.__m_p_name` |
> | Port Name | `port.__m_p_hwid` |
> | Serial Number | `port.__m_p_serial_number` |
> | Location | `port.__m_p_location` |
> | Manufacturer | `port.__m_p_manufacturer` |
> | Product | `port.__m_p_product` |
> | Interface | `port.__m_p_interface` |
>
> The only one placeholder that is not an attribute of the Port classes i `firmware` which represent the filename absolute
> path of the firmware to be uploaded
>
> | Value       | Placeholder |
> |------------|-------------|
> | Firmware | `firmware` |



#### Arancino Serial Ports

Configuration Section for Serial Port Type:

```ini
# default 'arancino port' configuration status
[port.serial]

# automatically connect a new discovered device
enabled = True

# set to true to make it not visible in the main device view in the UI
hide = False

# baudrate used for 'touch' reset
reset_baudrate = 300

# Filter works with the below list of VID:PID. Accepted filter type are: EXCLUDE, ONLY, ALL
# EXCLUDE: excludes the ones in the list.
# ONLY: acceptes only the ones in the list.
# ALL: no filter, accepts all. This is the default filter type.
filter_type=ALL

# List of VID:PID used to make a filter
filter_list = ["0x04d8:0xecd9", "0x04d8:0xecd9","0x04d8:0xecd9"]

# The command to run to do a firmware upload
upload_command = /usr/bin/run-bossac-cli {port._device} {firmware}
```

#### Arancino Test Ports
This is new in version `2.0.0` and it's used to make tests of Cortex commands, stress test or unit test:

```ini
[port.test]
# automatically enable (and connect) a new discovered port
enabled = True

# set to true to make it not visible in the main device view in the UI
hide = True

# Filter works with the below list of VID:PID. Accepted filter type are: EXCLUDE, ONLY, ALL
# EXCLUDE: excledus the ones in the list.
# ONLY: acceptes only the ones in the list.
# ALL: no filter, accepts all. This is the default filter type.
filter_type=ALL

# List of VID:PID used to make a filter
filter_list = []

# the number of port to create for test purpose
num = 0

# delay between each command in seconds (accept float). Default 500ms

delay = 0.5

# prefix of the id generated for the test port
id_template = TESTPORT

# command to be spawn when upload api is called. The command could have one or more placeholders.
upload_command =
```