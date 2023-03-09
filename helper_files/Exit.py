from structlog import BoundLogger

from helper_files.Action import Action
from helper_files.ConfigWrapper import ConfigWrapper


class Exit(Action):

    def __init__(self, logger: BoundLogger, config: ConfigWrapper, ip_address,SMTP_port, POP3_port, username, password):
        super().__init__(logger, config,ip_address,SMTP_port, POP3_port, username, password)
        pass

    def action(self):
        pass