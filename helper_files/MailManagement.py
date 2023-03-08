from structlog import BoundLogger

from helper_files.Action import Action
from helper_files.ConfigWrapper import ConfigWrapper


class MailManagement(Action):

    def __init__(self, logger: BoundLogger, config: ConfigWrapper):
        super().__init__(logger, config)
        pass

    def action(self):
        pass