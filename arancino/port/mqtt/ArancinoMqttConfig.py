from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig, ArancinoEnvironment, Singleton
from re import findall, match

@Singleton
class ArancinoMqttConfig:
    def __init__(self) -> None:
        self.__CONF = ArancinoConfig.Instance().cfg
        self.__ENV = ArancinoEnvironment.Instance()

        self.cnf = {
            "client_id" : self.__ENV.serial_number,
            # ! Issue : 123
            # "queue_size" : "<port.mqtt.queue_size>"
        }

        self.cnf |= {
            # region MQTT TOPICS
            "discovery_topic"   : "<port.mqtt.connection.discovery_topic>/{}".format(self.cnf["client_id"]),
            "cortex_topic"      : "<port.mqtt.connection.cortex_topic>/{}".format(self.cnf["client_id"]),
            "service_topic"     : "<port.mqtt.connection.service_topic>/{}".format(self.cnf["client_id"]),
            "conn_status_topic" : "<port.mqtt.connection.service_topic>/connection_status/{}".format(self.cnf["client_id"]),
            # endregion
        }


        self.cnf |= {
            "trace" : "<log.trace>", # Campo non presente nei file di configurazione

            "filter_list" : "<port.mqtt.filter_list>",
            "filter_type" : "<port.mqtt.filter_type>",
                
            # region CONNECTION CONFIG
            "username"  : "<port.mqtt.connection.username>",
            "password"  : "<port.mqtt.connection.password>",
            "host"      : "<port.mqtt.connection.host>",
            "port"      : "<port.mqtt.connection.port>",
            "use_tls"   : "<port.mqtt.connection.use_tls>",
            "ca_path"   : "<port.mqtt.connection.ca_path>",
            "cert_path" : "<port.mqtt.connection.cert_path>",
            "key_path"  : "<port.mqtt.connection.key_path>",
            "reset_on_connect" : "<port.mqtt.reset_on_connect>",
            "auto_enable"      : "<port.mqtt.auto_enable>",
            "hide"             : "<port.mqtt.hide>",
            # endregion

            # region TOPIC MQTT Port
            "cmd_from_mcu" : self.get("cortex_topic") + "/{}/cmd_from_mcu",
            "rsp_to_mcu"   : self.get("cortex_topic") + "/{}/rsp_to_mcu",
            "cmd_to_mcu"   : self.get("cortex_topic") + "/{}/cmd_to_mcu",
            "rsp_from_mcu" : self.get("cortex_topic") + "/{}/rsp_from_mcu",
            #endregion
        }

        self.__load()

        # ! Issue : 123
        # if self.cnf["queue_size"] is None:
        #     self.cnf["queue_size"] = 500

    def __load(self): 
        for key, value in self.cnf.items():
            self.cnf[key] = self.__format(value)

    def __format(self, path : str):
        regex = "<[^>]*>"

        if match(regex+"$", path): 
            return self.__get(path)
        else:
            find = findall(regex, path)
            if len(find) == 0: return path

            for elem in find:
                path = path.replace(elem, str(self.__get(elem)))
    
        return path
    
    def format(self, path):
        return self.__format(path)

    def __get(self, path : str):
        path = path.strip("<").strip(">").split(".")
        value = None
        
        for key in path:
            if value is None: value = self.__CONF.get(key)
            else: value = value.get(key)

        return value

    def get(self, key : str):
        return self.cnf[key.strip()] or None


if __name__ == "__main__":
    cfg = ArancinoMqttConfig.Instance()
