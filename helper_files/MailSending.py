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

    def _check_end_line(self,last_line: str) -> bool:
        #more robust way of checking end line -> not only valid when only stopping character,
        # but also when the stopping character is accompanied with spaces
        return_boolean = False
        if last_line:
            return_boolean = ''.join(list(filter(lambda x: x != self._config.get_stopping_character(), last_line))).isspace()
        return not return_boolean