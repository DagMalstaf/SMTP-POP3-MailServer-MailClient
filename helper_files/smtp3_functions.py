import socket
import pickle
from typing import List
from structlog import BoundLogger

from helper_files.ConfigWrapper import ConfigWrapper
from helper_files.MessageWrapper import MessageWrapper

"""
Function: smtp_helo(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, server_domain_name: str) -> None

Description:
This function is used to initiate an SMTP connection by sending the HELO command to the SMTP server. 
It takes a `BoundLogger` object, a `ConfigWrapper` object, a `socket` object representing the SMTP connection, and the domain name of the SMTP server as input. 
It sends the HELO command to the server and waits for a response, then logs either a success or error message based on the response.

Parameters:
- logger: A `BoundLogger` object used to log messages.
- config: A `ConfigWrapper` object used to obtain configuration values.
- smtp_socket: A `socket` object representing the SMTP connection.
- server_domain_name: A string containing the domain name of the client.

Returns:
None

Example Usage:
To initiate an SMTP connection using the HELO command, call the function like this: smtp_helo(logger, config, smtp_socket, host_domain_name)

"""
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

"""
Function: smtp_mail_from(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, from_address: str) -> None

Description:
This function is used to set the sender address of the email message by sending the MAIL FROM command to the SMTP server. 
It takes a `BoundLogger` object, a `ConfigWrapper` object, a `socket` object representing the SMTP connection, and the email address of the sender as input. 
It sends the MAIL FROM command to the server and waits for a response, then logs either a success or error message based on the response.

Parameters:
- logger: A `BoundLogger` object used to log messages.
- config: A `ConfigWrapper` object used to obtain configuration values.
- smtp_socket: A `socket` object representing the SMTP connection.
- from_address: A string containing the email address of the sender.

Returns:
None

Example Usage:
To set the sender address of an email message using the MAIL FROM command, call the function like this: smtp_mail_from(logger, config, smtp_socket, from_address)

"""
def smtp_mail_from(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, from_address: str) -> None:
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
    

"""
Function: smtp_rcpt_to(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, to_address: str) -> None

Description:
This function is used to set the recipient address of the email message by sending the RCPT TO command to the SMTP server. 
It takes a `BoundLogger` object, a `ConfigWrapper` object, a `socket` object representing the SMTP connection, and the email address of the recipient as input. 
It sends the RCPT TO command to the server and waits for a response, then logs either a success or error message based on the response.

Parameters:
- logger: A `BoundLogger` object used to log messages.
- config: A `ConfigWrapper` object used to obtain configuration values.
- smtp_socket: A `socket` object representing the SMTP connection.
- to_address: A string containing the email address of the recipient.

Returns:
None

Example Usage:
To set the recipient address of an email message using the RCPT TO command, call the function like this: smtp_rcpt_to(logger, config, smtp_socket, to_address)

"""
def smtp_rcpt_to(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, to_address: str) -> None:
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

"""
Function: smtp_data(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, data: MessageWrapper) -> None

Description:
This function is used to send an email message using the DATA command to the SMTP server. 
It takes a `BoundLogger` object, a `ConfigWrapper` object, a `socket` object representing the SMTP connection,
and a `MessageWrapper` object containing the email message data as input. 
It sends the DATA command to the server along with the message data, and waits for a response, then logs either a success or error message based on the response.

Parameters:
- logger: A `BoundLogger` object used to log messages.
- config: A `ConfigWrapper` object used to obtain configuration values.
- smtp_socket: A `socket` object representing the SMTP connection.
- data: A `MessageWrapper` object containing the email message data.

Returns:
None

Example Usage:
To send an email message using the DATA command, call the function like this: smtp_data(logger, config, smtp_socket, data)

"""
def smtp_data(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, data: MessageWrapper) -> None:
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

"""
Function: smtp_quit(logger: BoundLogger, config: ConfigWrapper, smtp_socket: socket, host_domain_name: str) -> None

Description:
This function is used to terminate the SMTP session by sending the QUIT command to the SMTP server. 
It takes a `BoundLogger` object, a `ConfigWrapper` object, a `socket` object representing the SMTP connection, and the hostname of the host as input. 
It sends the QUIT command to the server and waits for a response, then logs either a success or error message based on the response.

Parameters:
- logger: A `BoundLogger` object used to log messages.
- config: A `ConfigWrapper` object used to obtain configuration values.
- smtp_socket: A `socket` object representing the SMTP connection.
- host_domain_name: A string containing the hostname of the host.

Returns:
None

Example Usage:
To terminate the SMTP session by sending the QUIT command to the SMTP server, call the function like this: smtp_quit(logger, config, smtp_socket, host_domain_name)

"""
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
    else:
       logger.error(f"There was an error sending the QUIT command to {smtp_socket.getpeername()[0]} on port {smtp_socket.getpeername()[1]}")


