from typing import List
import socket
from helper_files.ConfigWrapper import ConfigWrapper


def smtp_helo(config: ConfigWrapper, domain_name_receiver: str, smtp_socket: socket) -> str:
    # TODO: see image with typical sequence to implement functionality
    # TODO: implement "incorrect format" responses as well if this function fails
    # TODO: see the error code image 220 -> domain of receiver
    command = "HELO " + domain_name_receiver + "\r\n"
    smtp_socket.send(command.encode())
    response = smtp_socket.recv(config.get_max_size_package_tcp).decode()
    return response


def smtp_mail_from(sender: str):
    # TODO: see image with typical sequence to implement functionality
    # TODO: implement "incorrect format" responses as well if this function fails
    pass


def smtp_rcpt_to( receiver: str):
    # TODO: see image with typical sequence to implement functionality
    # TODO: implement "incorrect format" responses as well if this function fails
    pass


def smtp_data(message_body: str):
    # TODO: see image with typical sequence to implement functionality
    pass


def smtp_quit(**kwargs):
    receiver = kwargs.get("receiver")
    # TODO: see image with typical sequence to implement functionality
    # TODO: not entirely sure that the argument receiver is necessary tbh
    pass


