from abc import ABC, abstractmethod

from structlog import BoundLogger
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from helper_files.ConfigWrapper import ConfigWrapper


class Action(ABC):

    def __init__(self, logger: BoundLogger, config: "ConfigWrapper", ip_address,SMTP_port, POP3_port, username):
        self._logger = logger
        self._config = config
        self._ip_address = ip_address
        self._SMTP_port = SMTP_port
        self._POP3_port = POP3_port
        self._username = username
        

    @abstractmethod
    def action(self):
        pass
