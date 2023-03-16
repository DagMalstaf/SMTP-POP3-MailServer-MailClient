from typing import List
import socket
import pickle
from helper_files.ConfigWrapper import ConfigWrapper
from structlog import BoundLogger
from helper_files.MessageWrapper import MessageWrapper

    
def smtp_helo(logger : BoundLogger, config: ConfigWrapper, smtp_socket: socket, server_domain_name: str) -> None:
    send_message = tuple("HELO", " " + f"{server_domain_name}\r\n")
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0]
    if command == "250 OK":
        logger.info("Connectionto SMTP server successful")
    else:
        logger.error("There was an error connecting to the SMTP server")

def smtp_mail_from(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, from_address: str) -> None:
    send_message = tuple("MAIL FROM:", f"<{from_address}>\r\n")
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0] 

    if command == "250":
        logger.info("Received mail from %s", from_address)
    else:
        logger.error("This is the incorrect response format")
    



def smtp_rcpt_to(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, to_address: str) -> None:
    send_message = tuple("RCPT TO:", f"<{to_address}>\r\n")
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0] 

    if command == "250":
        logger.info("Send mail to %s", to_address)
    else:
        logger.error("This is the incorrect response format")


def smtp_data(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, data: MessageWrapper) -> None:
    send_message = tuple("DATA", data)
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0] 

    if command == "250":
        logger.info("Mail sent successfully")
    else:
        logger.error("This is the incorrect response format")



def smtp_quit(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, server_domain_name: str) -> None:
    send_message = tuple("QUIT", f"{server_domain_name}\r\n")
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0]
    if command == "221":
        logger.info("Closed the connection to the SMTP server")
    else:
        logger.error("There was an error closing the SMTP server connection")


