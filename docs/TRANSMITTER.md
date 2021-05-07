## Introduction

From version `2.4.0` were introduced a new components in Arancino Module called *Transmitter*. Transmitter works to get
Times Series data from Redis and send them outside the edge devices.

Transmitter is composed of three main parts: _Reader_, _Parser_, _Sender_, that runs sequentially. Each parts can be configured
separately, but only _Parser_ and _Sender_ can be extended and customized.

### Reader
It's a thread that run periodically (see the specific configuration) and retrieves data from the 
[_Time Series Store_](CONFIGURATION.md#Redis Configuration) in Redis.


### Parser
Parser need to arrange and organize the data retrieved by the Reader. It can be extended and customized in base of the applications
needs. At the base it uses a template engine and a template file to format arranged data. By default exists 3 simple template file
- default.json.tmpl
- default.xml.tmpl
- default.yaml.tmpl


### Sender
It' the final step of the Transmitter component and it is used to send data outside the Arancino Module using standard
communications channels. The Senderd implementations are:
- TCP Socket
- MQTT