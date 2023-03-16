import socket
from typing import List

from structlog import BoundLogger

from helper_files.Action import Action
from helper_files.MessageWrapper import MessageWrapper
from helper_files.smtp3_functions import smtp_helo, smtp_mail_from, smtp_rcpt_to, smtp_data, smtp_quit
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from helper_files.ConfigWrapper import ConfigWrapper
# SMTP
class MailSending(Action):

    def __init__(self, logger: BoundLogger, config: "ConfigWrapper",ip_address,SMTP_port, POP3_port, username, password):
        super().__init__(logger, config, ip_address, SMTP_port, POP3_port, username, password)
        pass


    """
    Function: action(self)

    Description:
    This method is used to send a message using the SMTP protocols. 
    It prompts the user to enter the message content, verifies the message format using the `MessageWrapper` class. 
    Then sends the message using the `socket` module and the SMTP protocol. 
    The SMTP communication is performed using separate methods.

    Parameters:
    None

    Returns:
    None
    """
    def action(self):
        print("Enter mail, end with '.' on a single line by itself")
        correct_format = False
        while not correct_format:
            input_list: List[str] = list()
            while self._check_end_line(input_list[-1]):
                input_list.append(input())
            input_message = '\n'.join(input_list)

            message = MessageWrapper(self._logger,self._config, input_message)
            if message.verify_format():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as smtp_socket:
                    smtp_socket.bind((self._config.get_host(), self._SMTP_port))
                    smtp_socket.listen()
                    conn, addr = smtp_socket.accept()
                    with conn:
                        self._logger.info(f"{addr} Service Ready")
                        smtp_helo(self._logger, self._config, conn, self._config.get_host)
                        smtp_mail_from(self._logger, self._config, conn, message.getFrom)
                        smtp_rcpt_to(self._logger, self._config, conn,message.getTo())
                        smtp_data(self._logger, self._config, conn, message)
                        smtp_quit(self._logger, self._config, conn, self._config.get_host)
                        self._logger.info("Mail sent successfully")
                correct_format = True
            else:
                self._logger.error(f"This is an incorect format")
                self._logger.info(f"Please enter the correct format: {self._config.get_message_format()}")



    """
    Function: _check_end_line(self, last_line: str) -> bool

    Description:
    This method is used to check if the user has finished entering the message content. 
    It is a more robust way of checking end line -> not only valid when only stopping character,
    but also when the stopping character is accompanied with spaces.
    It takes the last line entered by the user as input, and checks if it is a blank line with only the stopping character. 
    The stopping character is obtained from the `ConfigWrapper` class.

    Parameters:
    - last_line: A string containing the last line of user input.

    Returns:
    A boolean value indicating whether the user has finished entering the message content.

    Example Usage:
    To check if the user has finished entering the message content, call the method like this: _check_end_line(last_line)

    """
    def _check_end_line(self,last_line: str) -> bool:  
        return_boolean = False
        if last_line:
            return_boolean = ''.join(list(filter(lambda x: x != self._config.get_stopping_character(), last_line))).isspace()
        return not return_boolean