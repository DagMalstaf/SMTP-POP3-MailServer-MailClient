import socket
import pickle
from typing import List
from structlog import BoundLogger

from helper_files.ConfigWrapper import ConfigWrapper
from helper_files.MessageWrapper import MessageWrapper
from custom_exceptions.RestartMailServerError import RestartMailServerError


def smtp_helo(logger : BoundLogger, config: ConfigWrapper, smtp_socket: socket, host_domain_name: str) -> None:
    logger.info(f"Sending HELO command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
    send_message = ("HELO", " " + f"{host_domain_name}\r\n")
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0]
    if command == "250 OK":
        logger.info("Success")
    else:
        logger.error(f"There was an error sending the HELO command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
        logger.error(f"Error: {tuple_data[1]}")
        smtp_quit(logger, config, smtp_socket, host_domain_name)


def smtp_mail_from(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, from_address: str, host_domain_name: str) -> None:
    logger.info(f"Sending MAIL FROM command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
    send_message = ("MAIL FROM:", f"<{from_address}>\r\n")
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0] 

    if command == "250":
        logger.info("Success")
    else:
        logger.error(f"There was an error sending the MAIL FROM command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
        logger.error(f"Error: {tuple_data[1]}")
        smtp_quit(logger, config, smtp_socket, host_domain_name)
    

def smtp_rcpt_to(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, to_address: str, host_domain_name: str) -> None:
    logger.info(f"Sending RCPT TO command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
    send_message = ("RCPT TO:", f"<{to_address}>\r\n")
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0] 

    if command == "250":
        logger.info("Success")
    else:
        logger.error(f"There was an error sending the RCPT TO command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
        logger.error(f"Error: {tuple_data[1]}")
        smtp_quit(logger, config, smtp_socket, host_domain_name)
    

def smtp_data(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, data: MessageWrapper, host_domain_name: str) -> None:
    logger.info(f"Sending DATA command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
    send_message: tuple = "DATA", data
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0] 

    if command == "250":
        logger.info("Mail sent successfully")
    else:
       logger.error(f"There was an error sending the DATA command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
       logger.error(f"Error: {tuple_data[1]}")
       raise RestartMailServerError
       
def smtp_quit(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, host_domain_name: str) -> None:
    logger.info(f"Sending QUIT command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
    send_message = ("QUIT", f"{host_domain_name}\r\n")
    pickle_data = pickle.dumps(send_message)
    smtp_socket.sendall(pickle_data)

    response_message = smtp_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    command = tuple_data[0]
    if command == "221":
        logger.info("Closed the connection to the SMTP server")
        raise RestartMailServerError
    else:
       logger.error(f"There was an error sending the QUIT command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")
       logger.error(f"Error: {tuple_data[1]}")


