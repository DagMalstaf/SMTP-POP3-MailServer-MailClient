from typing import Type, Dict

from structlog import BoundLogger

from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.Exit import Exit
from helper_files.MailManagement import MailManagement
from helper_files.MailSending import MailSending

CLIENT_MAIL_ACTIONS: Dict[str, Type[MailSending | MailManagement | Exit]] = {
    "Mail Sending": MailSending,
    "Mail Management": MailManagement,
    "Exit": Exit
}

def get_action(logger: BoundLogger, action: str) -> Type[MailSending | MailManagement | Exit]:
    try:
        return CLIENT_MAIL_ACTIONS.get(action)
    except KeyError as e:
        logger.info(f"Invalid action given for mail client: {action}")
        raise RestartMailServerError
        pass
