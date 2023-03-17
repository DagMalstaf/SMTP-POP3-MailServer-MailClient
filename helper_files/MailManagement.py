from structlog import BoundLogger
from typing import TYPE_CHECKING
import socket


from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.Action import Action
from typing import TYPE_CHECKING


from helper_files.functions.pop3_functions import pop3_LIST, pop3_USER, pop3_PASS, pop3_QUIT, pop3_DELE, pop3_RETR, pop3_STAT, pop3_authentication
if TYPE_CHECKING:
    from helper_files.ConfigWrapper import ConfigWrapper


class MailManagement(Action):

    def __init__(self, logger: BoundLogger, config: "ConfigWrapper",ip_address,SMTP_port, POP3_port, username):
        super().__init__(logger, config,ip_address,SMTP_port, POP3_port, username)
        pass

    def action(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pop3_socket:
            pop3_socket.bind((self._config.get_host(), self._POP3_port))
            pop3_socket.listen()
            self._logger.info(f"Waiting for connection on port:  {pop3_socket}")
            conn, addr = pop3_socket.accept()
            with conn:
                if pop3_authentication(conn):
                    self._logger.info("Authentication successful")
                    while True:
                        try:
                            action_string = input(f"Provide action to perform [{self._config.get_mail_management_actions_as_string()}]: ")
                            if action_string == "Quit":
                                pop3_QUIT(self._logger, self._config, conn)
                            elif action_string == "Status":
                                pop3_STAT()
                            elif action_string == "List":
                                pop3_LIST()
                            elif action_string == "Retrieve":
                                pop3_RETR()
                            elif action_string == "Delete":
                                pop3_DELE()
                            else:
                                self._logger.error(f"Invalid action: {action_string}")
                        except Exception as e:
                            self._logger.exception(f"An error occurred: {e}")        
                else:
                    raise RestartMailServerError("Restarting Mail Server")


    

