from multiprocessing import get_logger
from typing import Union, Dict

from helper_files.Action import Action
from helper_files.ConfigWrapper import ConfigWrapper

CLIENT_ACTIONS: Dict[str,Action] ={
    "Mail Sending": Action() ,
    "Mail Management": Action(),
    "Exit":Action()
}


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


def get_action_class(key:str):
    try:
        return CLIENT_ACTIONS.get(key)
    except KeyError as e:
        pass


def main():
    ip_address,SMTP_port, POP3_port, username, password = get_parameters_mail_client()
    while True:
        action = retrieve_command_promt_input(f"Please select action [{', '.join(CLIENT_ACTIONS.keys())}]: ")
        wrapper_class_mail_action = get_action_class(action)

if __name__ == "__main__":
    logger = get_logger()
    config = ConfigWrapper("general_config")
    main()
