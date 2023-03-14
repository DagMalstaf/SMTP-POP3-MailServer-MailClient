import socket
from typing import List

from structlog import BoundLogger

from helper_files.Action import Action
from helper_files.ConfigWrapper import ConfigWrapper
from helper_files.MessageWrapper import MessageWrapper
from helper_files.pop3_functions import pop3_helo, pop3_mail_from, pop3_rcpt_to, pop3_data, pop3_quit


class MailSending(Action):

    def __init__(self, logger: BoundLogger, config: ConfigWrapper,ip_address,SMTP_port, POP3_port, username, password):
        super().__init__(logger, config, ip_address,SMTP_port, POP3_port, username, password)
        pass


    """
    Function: action(self)

    Description:
    This method is used to send a message using the SMTP and POP3 protocols. 
    It prompts the user to enter the message content, verifies the message format using the `MessageWrapper` class. 
    Then sends the message using the `socket` module and the POP3 protocol. 
    The SMTP and POP3 communication is performed using separate methods.

    Parameters:
    None

    Returns:
    None
    """
    def action(self):
        print("Enter mail, end with '.' on a single line by itself")
        input_list: List[str] = list()
        while self._check_end_line(input_list[-1]):
            input_list.append(input())

        message = MessageWrapper(self._logger,self._config, '\n'.join(input_list))
        if message.verify_format():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pop3_socket:
                pop3_socket.bind((self._config.get_host(), self._POP3_port))
                pop3_socket.listen()
                conn, addr = pop3_socket.accept()
                with conn:
                    self._logger.info(f"Connected by {addr}")
                    pop3_helo(message.getToDomain_name())
                    pop3_mail_from(message.getFrom())
                    pop3_rcpt_to(message.getTo())
                    pop3_data(message.getMessageBody())
                    pop3_quit(receiver = message.getTo())


#
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