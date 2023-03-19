from structlog import BoundLogger
from typing import TYPE_CHECKING
import socket


from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.Action import Action
from typing import TYPE_CHECKING


from helper_files.functions.pop3_functions import pop3_LIST, pop3_QUIT, pop3_DELE, pop3_RETR, pop3_STAT, pop3_authentication
if TYPE_CHECKING:
    from helper_files.ConfigWrapper import ConfigWrapper


class MailManagement(Action):

    def __init__(self, logger: BoundLogger, config: "ConfigWrapper",ip_address,SMTP_port, POP3_port, username):
        super().__init__(logger, config,ip_address,SMTP_port, POP3_port, username)
        pass

    def action(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pop3_socket:
            pop3_socket.connect((self._ip_address, self._POP3_port))
            self._logger.info(f"Connected to POP3 server at port {self._POP3_port}")
            server_confirmation = pop3_socket.recv(self._config.get_max_size_package_tcp()).decode()
            self._logger.info(f"Server confirmation: {server_confirmation}")
            if pop3_authentication(self, pop3_socket):
                self._logger.info("Authentication successful")
                while True:
                    try:
                        action_string = input(f"Provide action to perform [{self._config.get_mail_management_actions_as_string()}]: ")
                        if action_string == "Quit":
                            pop3_QUIT(self._logger, self._config, pop3_socket)
                        elif action_string == "Status":
                            pop3_STAT(self._logger, self._config, pop3_socket)
                        elif action_string == "List":
                            pop3_LIST(self._logger, self._config, pop3_socket)
                        elif action_string == "Retrieve":
                            pop3_RETR(self._logger, self._config, pop3_socket)
                        elif action_string == "Delete":
                            pop3_DELE(self._logger, self._config, pop3_socket)
                        else:
                            self._logger.error(f"Invalid action: {action_string}")

                    
                    except Exception as e:
                        self._logger.exception(f"An error occurred: {e}")
                        raise e        
            else:
                self._logger.error("Authentication failed")
                raise RestartMailServerError("Restarting Mail Server")


    

