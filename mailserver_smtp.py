import socket
import threading
import pickle
import os

from helper_files.MessageWrapper import MessageWrapper
from concurrent.futures import ThreadPoolExecutor
from structlog import get_logger, BoundLogger
from helper_files.ConfigWrapper import ConfigWrapper

# define a semaphore so only 1 thread can access the mailbox.
mailbox_semaphore = threading.Semaphore(1)


def main() -> None:
    try:
        logger = get_logger()
        logger.info("Starting SMTP Server")
        listening_port = retrieve_port(logger)
        config = ConfigWrapper(logger, "general_config")
        loop_server(logger, config, listening_port)
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")


def retrieve_port(logger: BoundLogger) -> int:
    try:
        my_port = int(input("Enter a port number (non-privileged ports are > 1023): "))
        if my_port > 1023:
            return my_port
        
        else:
            logger.error(f"Error: port number must be > 1023")
            return retrieve_port(logger)
    except ValueError as e:
        logger.error(f"Error: {e}")
        return retrieve_port(logger)
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")


def loop_server(logger: BoundLogger, config: ConfigWrapper, port: int) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as smtp_socket:
            smtp_socket.bind((config.get_host(), port))
            smtp_socket.listen()
            logger.info(f"Listening on port {port}")
            while True:
                try:
                    conn, addr = smtp_socket.accept()
                    logger.info(f"{addr} Client connected")
                    thread = threading.Thread(target=handle_client, args=(logger, config, conn))
                    thread.start()

                except ConnectionResetError:
                    logger.exception("Client closed the connection unexpectedly")
                except socket.timeout:
                    logger.exception("No data received from client within timeout period")
                    send_message = ("554", "No data received from client within timeout period"+ "\r\n")
                    pickle_data = pickle.dumps(send_message)
                    conn.sendall(pickle_data)
                except ValueError:
                    logger.exception("Received data cannot be converted to string")
                    send_message = ("554", "Received data cannot be converted to string"+ "\r\n")
                    pickle_data = pickle.dumps(send_message)
                    conn.sendall(pickle_data)
                except KeyboardInterrupt:
                    logger.exception("Program interrupted by user")
                    send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
                    pickle_data = pickle.dumps(send_message)
                    conn.sendall(pickle_data)
                except Exception as e:
                    logger.exception(f"An error occurred: {e}")
                    send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
                    pickle_data = pickle.dumps(send_message)
                    conn.sendall(pickle_data)

def handle_client(logger: BoundLogger, config: ConfigWrapper, conn: socket) -> None:
    try:
        while True:
            data = conn.recv(config.get_max_size_package_tcp())
            if not data:
                logger.error("Client disconnected unexpectedly")
                break
            logger.info(f"Received data from {conn.getpeername()}")
            tuple_data = pickle.loads(data)
            command = tuple_data[0]
            data = tuple_data[1]
            if command == "QUIT":
                SMTP_QUIT(logger, config, command, data, conn)
                return
            command_handler(logger, config, command, data, conn)
        
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        conn.sendall(pickle_data)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        conn.sendall(pickle_data)




def command_handler(logger: BoundLogger, config: ConfigWrapper, command: str, message: str,
                    connection: socket) -> None:
    logger.info(f"Received command: {command}")
    try:
        if command == "HELO":
            SMTP_HELO(logger, config, command, message, connection)
        elif command == "MAIL FROM:":
            SMTP_MAIL_FROM(logger, config, command, message, connection)
        elif command == "RCPT TO:":
            SMTP_RCPT_TO(logger, config, command, message, connection)
        elif command == "DATA":
            SMTP_DATA(logger, config, command, message, connection)
        elif command == "QUIT":
            SMTP_QUIT(logger, config, command, message, connection)
        else:
            logger.info(f"Invalid command: {command}")
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)


"""
Function: SMTP_HELO(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket, executor: ThreadPoolExecutor) -> None

Description:
This function handles the "HELO" command for the SMTP server. 
It sends a welcome message to the client, along with a status code of 250 OK. 
The welcome message includes the client's hostname, which is passed as the "message" parameter.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve server settings.
- command (str): The SMTP command being executed (e.g. "HELO", "MAIL FROM", "RCPT TO", "DATA", etc.).
- message (str): The client's hostname, passed as a parameter to the "HELO" command.
- connection (socket): The client's connection to the server.
- executor (ThreadPoolExecutor): A thread pool executor to manage multiple threads.

Returns:
None

Example Usage:
To handle the "HELO" command for the SMTP server, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
connection, address = smtp_socket.accept()
command = "HELO"
message = "example.com"
executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
SMTP_HELO(logger, config, command, message, connection, executor)

"""


def SMTP_HELO(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    try:
        logger.info(command + message)
        send_message = ("250 OK", "Hello " + message + "\r\n")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)


"""
Function: SMTP_MAIL_FROM(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None

Description:
This function handles the "MAIL FROM" command for the SMTP server. 
It acknowledges the sender's email address by returning a status code of 250 along with a message confirming that the sender is accepted.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve server settings.
- command (str): The SMTP command being executed (e.g. "HELO", "MAIL FROM", "RCPT TO", "DATA", etc.).
- message (str): The email address of the sender.
- connection (socket): The client's connection to the server.

Returns:
None

Example Usage:
To handle the "MAIL FROM" command for the SMTP server, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
connection, address = smtp_socket.accept()
command = "MAIL FROM"
message = "johndoe@example.com"
SMTP_MAIL_FROM(logger, config, command, message, connection)

"""


def SMTP_MAIL_FROM(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    try:
        logger.info(command + message)
        send_message = ("250", " " + message + "... Sender ok" + "\r\n")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)


"""
Function: SMTP_RCPT_TO(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None

Description:
This function handles the "RCPT TO" command for the SMTP server. 
It acknowledges the recipient's email address by returning a status code of 250 along with a message confirming that the recipient is accepted.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve server settings.
- command (str): The SMTP command being executed (e.g. "HELO", "MAIL FROM", "RCPT TO", "DATA", etc.).
- message (str): The email address of the recipient.
- connection (socket): The client's connection to the server.

Returns:
None

Example Usage:
To handle the "RCPT TO" command for the SMTP server, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
connection, address = smtp_socket.accept()
command = "RCPT TO"
message = "janedoe@example.com"
SMTP_RCPT_TO(logger, config, command, message, connection)

"""


def SMTP_RCPT_TO(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    try:
        logger.info(command + message)
        send_message = ("250", " " + " root... Recipient ok" + "\r\n")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)


"""
Function: SMTP_DATA(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None

Description:
This function handles the "DATA" command for the SMTP server. 
It prompts the client to enter the message to be sent, 
writes the message to the recipient's mailbox, and confirms that the message has been accepted for delivery.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve server settings.
- command (str): The SMTP command being executed (e.g. "HELO", "MAIL FROM", "RCPT TO", "DATA", etc.).
- message (str): The message to be sent to the recipient.
- connection (socket): The client's connection to the server.

Returns:
None

Example Usage:
To handle the "DATA" command for the SMTP server, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
connection, address = smtp_socket.accept()
command = "DATA"
message = "Hello Jane, how are you?"
SMTP_DATA(logger, config, command, message, connection)

"""


def SMTP_DATA(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    try:
        logger.info(command)
        logger.info("354 Enter Mail, end with '.' on a line by itself")
        write_to_mailbox(logger, config, message, mailbox_semaphore, connection)
        send_message = ("250", " OK message accepted for delivery" + "\r\n")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)


"""
Function: SMTP_QUIT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None

Description:
This function handles the "QUIT" command for the SMTP server. 
It sends a closing message to the client and then closes the connection.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve server settings.
- command (str): The SMTP command being executed (e.g. "HELO", "MAIL FROM", "RCPT TO", "DATA", etc.).
- message (str): The message to be sent to the client upon closing the connection.
- connection (socket): The client's connection to the server.

Returns:
None

Example Usage:
To handle the "QUIT" command for the SMTP server, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
connection, address = smtp_socket.accept()
command = "QUIT"
message = "Goodbye!"
SMTP_QUIT(logger, config, command, message, connection)

"""


def SMTP_QUIT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    try:
        logger.info(command)
        send_message = ("221", message + " Closing Connection" + "\r\n")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
        connection.close()
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    
    finally:
        connection.close()


"""
Function: write_to_mailbox(logger: BoundLogger, config: ConfigWrapper, message: MessageWrapper, file_semaphore: threading.Semaphore) -> None

Description:
This function writes a message to the specified user's mailbox file. 
It first acquires a semaphore to ensure that the file is not being written to by another thread. 
It then opens the mailbox file in append mode and writes the message to the file. Finally, it releases the semaphore.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve the directory path where mailbox files are stored.
- message (MessageWrapper): A message object containing the message to be written to the mailbox file.
- file_semaphore (threading.Semaphore): A semaphore used to synchronize access to the mailbox file.

Returns:
None

Example Usage:
To write a message to a user's mailbox file, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
message = MessageWrapper("JohnDoe", "JaneDoe", "Hello World", "3/16/2023")
file_semaphore = threading.Semaphore()
write_to_mailbox(logger, config, message, file_semaphore)

"""


def write_to_mailbox(logger: BoundLogger, config: ConfigWrapper, message: MessageWrapper,
                     file_semaphore: threading.Semaphore, connection: socket) -> None:
    try:
        mail_address = message.get_to().strip()
        logger.debug(f"this is the username: {mail_address}")

        file_semaphore.acquire()
        mailbox_file = os.path.join("USERS", mail_address, "my_mailbox.txt")

        with open(mailbox_file, 'a') as file:
            file.write(str(message) + '\n\n')
            file.flush()

    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)

    
    finally:
        file_semaphore.release()




if __name__ == "__main__":
    main()
