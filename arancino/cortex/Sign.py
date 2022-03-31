from arancino.ArancinoConstants import ArancinoCommandResponseCodes, ArancinoCommandErrorCodes
from arancino.ArancinoExceptions import ArancinoException
from arancino.cortex.CortexCommandExectutor import CortexCommandExecutor
from arancino.cortex.ArancinoPacket import ArancinoCommand, ArancinoResponse
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
from arancino.cortex.ArancinoPacket import PACKET
from datetime import datetime


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()


class Sign(CortexCommandExecutor):

    def __init__(self, arancinoCommand: ArancinoCommand):
        self.arancinoCommand = arancinoCommand
        self.arancinoResponse = ArancinoResponse(packet=None)

    def execute(self):
        # TODO fai la magia
        pass

    def _check(self):
        """
        esegui controlli sui parametri della comando SIGN.
        """
        pass
