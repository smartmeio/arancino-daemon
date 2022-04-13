import configparser, os, json
from arancino.transmitter.ComponentsFactory import ReaderFactory, ParserFactory, SenderFactory
from arancino.utils.ArancinoUtils import stringToBool, ArancinoLogger, ArancinoConfig

LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()

class Flow:

    def __init__(self, flowname):
        self.__name = flowname
        self.__cfg_file_name = "transmitter.flow.{}.cfg".format(flowname)

        self.__is_loaded = False
        self.__is_enabled = False

        self.__reader = ReaderFactory().getReader()

        self.__parser = None
        self.__parser_class_name = None
        self.__parser_config = None

        self.__sender = None
        self.__parser_class_name = None
        self.__sender_config = None

        self.__load_cfg()
        self.__load_cmp()

    def __load_cfg(self):
        try:
            # Retrieve arancino config path from Env Vars
            arancino_config_path = os.environ.get('ARANCINOCONF')

            # Read Flow the configuration file
            config = configparser.ConfigParser()
            config.read(os.path.join(arancino_config_path, self.__cfg_file_name))

            # Retrieve is the Flow is enabled or disabled
            self.__is_enabled = stringToBool(config.get("flow", "enabled"))

            # Flow Component to use in reflection method
            self.__parser_class_name = config.get("parser", "class")
            self.__sender_class_name = config.get("sender", "class")

            # Config to be sent to the Flow Components
            parser_sections_name_list = json.loads(config.get("parser", "section"))
            sender_sections_name_list = json.loads(config.get("sender", "section"))

            # Convert ini sections into Dict
            self.__parser_config = {s: dict(config.items(s)) for s in parser_sections_name_list}
            self.__sender_config = {s: dict(config.items(s)) for s in sender_sections_name_list}
        except Exception as ex:
            LOG.error("{}Error while loading configuration of the Transmitter Flow {}: {}".format(self.__log_prefix, self.name, str(ex)), exc_info=TRACE)

    def __load_cmp(self):
        try:
            # Call factory methods with configs, to get instances of Sender and Parser

            pFactory = ParserFactory()
            sFactory = SenderFactory()

            self.__parser = pFactory.getParser(self.__parser_class_name, self.__parser_config)
            self.__sender = sFactory.getSender(self.__sender_class_name, self.__sender_config)

            self.__reader.attachHandler(self.update)
            self.__is_loaded = True

        except Exception as ex:

            self.__is_loaded = False

    @property
    def name(self):
        return self.__name


    @property
    def cfg_file_name(self):
        return self.__cfg_file_name


    @property
    def is_loaded(self):
        """
        True when this Flow is correctly loaded and instanced in all of its components, False otherwise

        :return: Boolean
        """
        return self.__is_loaded


    @property
    def is_enabled(self):
        """
        True if this Flow is enabled by the configuration, False otherwise

        :return: Boolean
        """
        return self.__is_enabled


    @property
    def reader(self):
        """
        The Reader Component instance
        :return: Reader
        """

        return self.__reader


    @property
    def parser(self):
        """
        The Parser Component instance used by this Flow
        :return: Parser
        """
        return self.__parser


    @property
    def sender(self):
        """
        The Sender Component instance used by this Flow
        :return: Sender
        """
        return self.__sender


    def stop(self):
        """
        Stops all the Components of this Flow
        :return: void
        """
        self.__reader.stop()
        self.__parser.stop()
        self.__sender.stop()


    def start(self):
        """
        Starts all the Components of this Flow
        :return: void
        """


        if not self.__reader.is_alive():
            self.__reader.start()
        self.__parser.start()
        self.__sender.start()


    def update(self, data):
        """
        Update method of the "Observer" (this Flow) used to be notified of generated
            data by the "Subject" (the Reader Component)
        :param data:
        :return: void
        """

        # Ex __do_elaboration(data)
        parsed_data, parsed_metadata = self.__parser.parse(data)

        # send data only if parsing is ok.
        if parsed_data:

            for index, segment_to_send in enumerate(parsed_data):
                sent = self.__sender.send(segment_to_send, parsed_metadata[index])

                # if parsing
                if sent:
                    # DO update the time series calling "ack" of the Reader
                    self.__reader.ack(parsed_metadata[index])
                else:
                    # DO NOT update timestamp in the time series
                    return

        else:
            # DO NOT update timestamp in the time series
            pass

