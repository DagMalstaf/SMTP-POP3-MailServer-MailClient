from abc import ABC, abstractmethod

from structlog import BoundLogger

from helper_files.ConfigWrapper import ConfigWrapper


class Action(ABC):

    def __init__(self, logger: BoundLogger, config: ConfigWrapper):
        self._logger = logger
        self._config = config

    @abstractmethod
    def action(self):
        pass
