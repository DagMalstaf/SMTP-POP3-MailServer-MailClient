from structlog import BoundLogger
from multiprocessing import get_logger
from typing import Union, Dict

from helper_files.Action import Action
from helper_files.ConfigWrapper import ConfigWrapper




def retrieve_command_promt_input(message_to_display:str, cast_to_int: bool = False, hash_input: bool = False) -> Union[str,int]:
    try:
        command_prompt_input = input(message_to_display)
        if cast_to_int:
            command_prompt_input = int(command_prompt_input)
        if hash_input:
            # using extra string to concatenate before hash to avoid dictionary attacks
            pass
        return command_prompt_input
    except:
        pass


def get_parameters_mail_client() -> tuple[str | int, str | int, str | int, str | int, str | int]:
    server_ip = retrieve_command_promt_input("Give IP address to connect to: ")
    SMTP_server_port = retrieve_command_promt_input("Give SMTP server port: ", cast_to_int=True)
    POP3_server_port = retrieve_command_promt_input("Give pop3 server port: ", cast_to_int=True)
    username = retrieve_command_promt_input("Provide username of mail account: ")
    password = retrieve_command_promt_input(" Provide password of mail account: ", hash_input=True)
    return server_ip, SMTP_server_port, POP3_server_port, username, password


def main(logger: BoundLogger, config: ConfigWrapper ):
    ip_address,SMTP_port, POP3_port, username, password = get_parameters_mail_client()
    while True:
        try:
            action = retrieve_command_promt_input(f"Please select action [{config.get_mail_client_actions_as_string()}]: ")
            wrapper_class_mail_action = config.get_mail_client_action_as_class(action)(logger, config)
            logger.info(f"succesfully starting {wrapper_class_mail_action} action")
            wrapper_class_mail_action.action()
        except:
            pass

if __name__ == "__main__":
    logger = get_logger()
    config = ConfigWrapper(logger,"general_config")
    main(logger,config)
