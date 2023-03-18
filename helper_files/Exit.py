from structlog import BoundLogger
import sys
import time

from helper_files.Action import Action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from helper_files.ConfigWrapper import ConfigWrapper


class Exit(Action):

    def __init__(self, logger: BoundLogger, config: "ConfigWrapper", ip_address,SMTP_port, POP3_port, username):
        super().__init__(logger, config,ip_address,SMTP_port, POP3_port, username)
        pass

    def action(self):
        self._logger.info(f"User {self._username} has logged out")
        self._logger.info(f"Program will exit in 3 seconds")
        time.sleep(1)
        self._logger.info("3")
        time.sleep(1)
        self._logger.info("2")
        time.sleep(1)
        self._logger.info("1")
        self._logger.info("Mail Client is shutting down")
        time.sleep(2)
        sys.exit()
