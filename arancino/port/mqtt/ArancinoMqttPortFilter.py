
from arancino.port.ArancinoPortFilter import ArancinoPortFilter

class ArancinoMqttPortFilter(ArancinoPortFilter):


    def __init__(self):
        pass


    def filterAll(self, ports={}, list=[]):
        return ports


    def filterExclude(self, ports={}, list=[]):
        # Do nothing
        return ports


    def filterOnly(self, ports={}, list=[]):
        # Do nothing
        return ports