from typing import List
import socket


def smtp_helo(smtp_socket: socket, server_domain_name: str) -> str:
    # TODO: see image with typical sequence to implement functionality
    # TODO: implement "incorrect format" responses as well if this function fails
    # TODO: see the error code image 220 -> domain of receiver
    helo_command = "HELO " + server_domain_name
    smtp_socket.send(helo_command.encode())
    response = smtp_socket.recv(1024)
    return response.decode()


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


