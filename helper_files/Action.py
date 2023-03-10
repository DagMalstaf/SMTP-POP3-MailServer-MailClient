from abc import ABC, abstractmethod

from structlog import BoundLogger

from helper_files.ConfigWrapper import ConfigWrapper


class Action(ABC):

    def __init__(self, logger: BoundLogger, config: ConfigWrapper, ip_address,SMTP_port, POP3_port, username, password):
        self._logger = logger
        self._config = config
        self._ip_address = ip_address
        self._SMTP_port = SMTP_port
        self._POP3_port = POP3_port
        self._username = username
        self._password = password

    @abstractmethod
    def action(self):
        pass
