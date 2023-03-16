from typing import List

from structlog import BoundLogger
import socket

from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.Action import Action
from typing import TYPE_CHECKING

from helper_files.helper_functions import retrieve_command_promt_input
from helper_files.pop3_functions import pop3_authentication, pop3_list
from helper_files.pop3_functions import pop3_stat, pop3_list, pop3_retrieve, pop3_delete, pop3_count
if TYPE_CHECKING:
    from helper_files.ConfigWrapper import ConfigWrapper


class MailManagement(Action):

    def __init__(self, logger: BoundLogger, config: "ConfigWrapper",ip_address,SMTP_port, POP3_port, username, password):
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
            raise RestartMailServerError("Restarting Mail Server")
        self._password = retrieve_command_promt_input("Password: ", hash_input=True)
        if self._password == "q":
            raise RestartMailServerError("Restarting Mail Server")
        self.action()