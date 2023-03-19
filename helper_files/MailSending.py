import socket
from typing import List
from typing import TYPE_CHECKING
from structlog import BoundLogger

from helper_files.Action import Action
from helper_files.MessageWrapper import MessageWrapper
from helper_files.smtp3_functions import smtp_helo, smtp_mail_from, smtp_rcpt_to, smtp_data, smtp_quit


if TYPE_CHECKING:
    from helper_files.ConfigWrapper import ConfigWrapper


class MailSending(Action):

    def __init__(self, logger: BoundLogger, config: "ConfigWrapper",ip_address,SMTP_port, POP3_port, username):
        super().__init__(logger, config, ip_address, SMTP_port, POP3_port, username)
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
        self._logger.info("Enter mail format line per line, end with '.' on a single line by itself")
        correct_format = False
        while not correct_format:
            input_list = list()
            input_list.append(input())
            while self._check_end_line(input_list[-1]):
                input_list.append(input())
            input_message = self._config.get_end_line_character().join(input_list)

            message = MessageWrapper(self._logger,self._config, input_message)
            if message.verify_format():
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as smtp_socket:
                    try:
                        smtp_socket.connect((self._ip_address, self._SMTP_port))
                        self._logger.info(f"Connected to SMTP server at port {self._SMTP_port}")
                        smtp_helo(self._logger, self._config, smtp_socket, self._config.get_host)
                        smtp_mail_from(self._logger, self._config, smtp_socket, message.get_from(), self._config.get_host)
                        smtp_rcpt_to(self._logger, self._config, smtp_socket, message.get_to())
                        smtp_data(self._logger, self._config, smtp_socket, message)
                        smtp_quit(self._logger, self._config, smtp_socket, self._config.get_host)
                        self._logger.info("Mail sent successfully")

                    except Exception as e:
                        self._logger.error(f"Error: {e}")
                        raise e
                correct_format = True
            else:
                self._logger.error(f"This is an incorect format")
                self._logger.info(f"Please enter the correct format:\n {self._config.get_message_format()}")



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
        if last_line.strip() and all(c in (' ', '.') for c in last_line.strip()):
            return_boolean = True
            return not return_boolean
        if last_line:
            return_boolean = ''.join(list(filter(lambda x: x != self._config.get_stopping_character(), last_line))).isspace()
        return not return_boolean
    
   
