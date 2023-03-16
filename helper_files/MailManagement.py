from structlog import BoundLogger
from typing import TYPE_CHECKING
import socket


from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.Action import Action
from typing import TYPE_CHECKING

from helper_files.functions.general_helper_functions import retrieve_command_promt_input
from helper_files.functions.pop3_functions import pop3_authentication, pop3_LIST, pop3_USER, pop3_PASS
if TYPE_CHECKING:
    from helper_files.ConfigWrapper import ConfigWrapper


class MailManagement(Action):

    def __init__(self, logger: BoundLogger, config: "ConfigWrapper",ip_address,SMTP_port, POP3_port, username):
        super().__init__(logger, config,ip_address,SMTP_port, POP3_port, username)
        pass


    
    

    def action(self):
        self._logger.info(f"Starting Mail Management")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pop3_socket:
            pop3_socket.bind((self._config.get_host(), self._POP3_port))
            pop3_socket.listen()
            conn, addr = pop3_socket.accept()
            with conn:
                if pop3_authentication(conn):
                    self._logger.info("Authentication successful")

                    while True:
                        action_string = input(f"Provide action to perform [{self._config.get_mail_management_actions_as_string()}]: ")
                        action = self._config.get_mail_management_action_as_fuction(action_string)
                        action(**self._get_kwargs())
                else:
                    raise RestartMailServerError("Restarting Mail Server")



    def pop3_authentication(self, connection) -> bool:
        try:
            while True:
                user_authentication_response = pop3_USER(self._logger, self._config, connection, username)
                if not user_authentication_response:
                    self._logger.info("User authentication failed")
                    username = retrieve_command_promt_input("Please enter your correct username or 'quit' to terminate : ")
                    if username == "quit":
                        return False
                    continue
                else:
                    self._logger.info("User authentication successful")
                    password = retrieve_command_promt_input("Provide password of mail account or 'quit' to terminate : ", hash_input=True)
                    if password == "quit":
                        return False
                    else:
                        pass_authentication_response = pop3_PASS(self._logger, self._config, connection, password)
                        if not pass_authentication_response:
                            self._logger.info("Password authentication failed")
                            password = retrieve_command_promt_input("Please enter your correct password or 'quit' to terminate : ")
                            if password == "quit":
                                return False
                            continue
                        else:
                            self._logger.info("Password authentication successful")
                            return True
        except:
            return False


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