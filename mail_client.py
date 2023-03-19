from structlog import BoundLogger
import structlog

from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.ConfigWrapper import ConfigWrapper
from helper_files.functions.general_helper_functions import get_parameters_mail_client, retrieve_command_promt_input
from helper_files.functions.mail_functions import get_action

def serve_forever(logger: BoundLogger, config: ConfigWrapper ):
    ip_address, SMTP_port, POP3_port, username = get_parameters_mail_client(logger)
    action = str()
    while True:
        try:
            action = retrieve_command_promt_input(f"Please select action [{config.get_mail_client_actions_as_string()}]: ", logger)
            wrapper_class_mail_action = get_action(logger,action)(logger, config,ip_address,SMTP_port, POP3_port, username)
            logger.info(f"Succesfully starting {action} action")
            wrapper_class_mail_action.action()
        except Exception as e:
            logger.error(f"An error occurred while executing {action} action", exc_info=True)
            raise e


def main() -> None:
    logger = structlog.get_logger()
    logger.info("Starting mail client")
    config = ConfigWrapper(logger,"general_config")
    try:
        serve_forever(logger,config)
    except RestartMailServerError as e:
        logger.info("Restarting mail client")
        main()


if __name__ == "__main__":
    main()
