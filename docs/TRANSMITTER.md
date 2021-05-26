## Introduction

From version `2.4.0` a new component has been introduced in Arancino Daemon called *Transmitter*. Transmitter works to get Times Series data from Redis and send them outside the edge devices.

Transmitter is composed of three main parts: _Reader_, _Parser_, _Sender_, that runs sequentially. Each part can be configured separately, but only _Parser_ and _Sender_ can be extended and customized.

## Reader
It's a thread that run periodically (see the specific configuration) and retrieves data from the 
[_Time Series Store_](CONFIGURATION.md#Redis Configuration) in Redis. This thread provides also the data aggregation based on the tags retrieved from the [_Tag Store_](CONFIGURATION.md#Redis Configuration) in Redis.

```ini
[transmitter.reader]
# Represents the time (in seconds) in which the reader collects data
# and transfers it to the upper level
cycle_time = 10
```


## Parser
Parser arranges and organizes the data retrieved by the Reader. It can be extended and customized according to the applications needs. At the base it uses a template engine and a template file to format arranged data. By default  3 simple template file are provided
- default.json.tmpl
- default.xml.tmpl
- default.yaml.tmpl


## Sender
It' the final step of the Transmitter component and it is used to send data outside the Arancino Daemon using standard
communications channels. The Sender implementations are:
- TCP Socket
- MQTT

> For each implementation of the three components there is a configuration region in the `arancino.cfg` file.

## Native Implementations

There are two stacks already implemented:
- _Simple Stack_ 
- _S4T Stack_

### Simple Stack

It is composed by the _Parser Simple_ which configured with one of the three default templates formats the data. 

```ini
[transmitter.parser]
class = ParserSimple

# template file used to parse data with the template engine (jinja2)
#   default available templates:
#   - default.yaml.tmpl
#   - default.json.tmpl
#   - default.xml.tmpl

file = default.json.tmpl

[transmitter.parser.simple]
# Configuration for ParserSimple
```

Then these formatted data can be sent with the _SenderMqtt_ or the _SenderTcpSocket_ specifing the parameters in the `arancino.cfg` as follow

```ini
[transmitter.sender]
# Available Senders are: SenderDoNothing, SenderTcpSocket, SenderMqtt, SenderMqttS4T
class = SenderDoNothing

[transmitter.sender.donothing]

[transmitter.sender.tcpsocket]
host = your_host.it
port = 1476

[transmitter.sender.mqtt]
use_tls = False
qos = 1
retain = False
topic = your_topic

# plain
host = your_host.it
port = 1883
username = your_username
password = your_password

# secure
ca_path =
cert_path =
key_path =
```

### S4T Stack

This stack implements the data flow of S4T as described here (https://wiki.smartme.io/schema_misure.pdf) in the section _Modalità semplice – lista_

The name of the time series key has to be composed as follow:

_\<measurement\>/\<field\>/\<click_slot_number\>_

Moreover you have to specify the influx database where the data will be stored

```ini
[transmitter.parser.s4t]
# Configuration for ParserS4T

db_name = db_name
```





