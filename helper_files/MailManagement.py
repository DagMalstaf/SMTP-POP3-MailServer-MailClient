from typing import List

from structlog import BoundLogger
import socket
from helper_files.Action import Action
from helper_files.ConfigWrapper import ConfigWrapper
from helper_files.pop3_functions import pop3_authentication, pop3_list
from mail_client import retrieve_command_promt_input, main


class MailManagement(Action):

    def __init__(self, logger: BoundLogger, config: ConfigWrapper,ip_address,SMTP_port, POP3_port, username, password):
        super().__init__(logger, config,ip_address,SMTP_port, POP3_port, username, password)
        pass

    def _get_kwargs(self):
        return {
            "username": self._username,
            "password": self._password
        }
    def action(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pop3_socket:
            pop3_socket.bind((self._config.get_host(), self._POP3_port))
            pop3_socket.listen()
            conn, addr = pop3_socket.accept()
            with conn:
                if pop3_authentication(**self._get_kwargs()):
                    pop3_list(**self._get_kwargs())

                    while True:
                        action_string = input(f"Provide action to perform [{self._config.get_mail_management_actions_as_string()}]: ")
                        action = self._config.get_mail_management_action_as_fuction(action_string)
                        action(**self._get_kwargs())
                else:
                    self._request_new_credentials()

    def _request_new_credentials(self) -> None:
        print("Authentication unsuccessful")
        print("Provide new credentials or q to restart")
        self._username = retrieve_command_promt_input("Username: ")
        if self._username == "q":
            main(self._logger, self._config)
            exit()
        self._password = retrieve_command_promt_input("Password: ", hash_input=True)
        if self._password == "q":
            main(self._logger, self._config)
            exit()
        self.action()