from typing import List
import socket
import pickle
from helper_files.ConfigWrapper import ConfigWrapper

    # TODO: see image with typical sequence to implement functionality
    # TODO: implement "incorrect format" responses as well if this function fails
    # TODO: see the error code image 220 -> domain of receiver
def smtp_helo(smtp_socket: socket, server_domain_name: str, config: ConfigWrapper) -> str:
    send_message = tuple("HELO", server_domain_name)
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response)
    command = tuple_data[0]
    message = tuple_data[1]
    if command == "250 OK":
        return str(command) + " " + str(message)
    else:
        return "ERROR: " + str(command) + " " + str(message)

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


