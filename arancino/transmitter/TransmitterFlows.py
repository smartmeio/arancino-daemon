from abc import ABC, abstractmethod
from TransmitterFactories import ReaderFactories, ParserFactory, SenderFactories
from arancino.transmitter.reader import Reader
from arancino.transmitter.parser import Parser
from arancino.transmitter.sender import Sender



class TransmitterFlowTemplate(ABC):

    @property
    def __reader(Reader):
        return ReaderFactories().getReader()

    @property
    @abstractmethod
    def __parser(Parser):
        pass

    @property
    @abstractmethod
    def __sender(Sender):
        pass

    @abstractmethod
    def load_configuration(self):
        pass

    def stop(self):
        self.__reader.stop()
        self.__parser.stop()
        self.__sender.stop()

    def start(self):
        self.__reader.start()
        self.__parser.start()
        self.__sender.start()

    def update(self, data):
        self.__do_elaboration(data)

    def __do_elaboration(self, data):

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


class FlowSmartme(TransmitterFlowTemplate):

    def __init__(self):
        __sender = SenderFactories.getSender(Sender.SenderKind.SENDER_DO_NOTHING)
        __parser = ParserFactory.getParser(Parser.ParserKind.PARSER_SIMPLE)
        self.__reader.attachHandler(self)

    def load_configuration(self):
        # todo
        pass


class FlowClient(TransmitterFlowTemplate):

    def __init__(self):
        __sender = SenderFactories.getSender(Sender.SenderKind.SENDER_DO_NOTHING)
        __parser = ParserFactory.getParser(Parser.ParserKind.PARSER_SIMPLE)
        self.__reader.attachHandler(self)

    def load_configuration(self):
        # todo
        pass