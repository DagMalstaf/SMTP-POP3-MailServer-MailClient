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

"""
Function: main() -> None

Description:
This is the main function of the program. 
It obtains a listening port using the `retrieve_port()` function, initializes a logger and a `ConfigWrapper` object, 
creates a `ThreadPoolExecutor` object, and calls the `loop_server()` function to start the server loop. 

Parameters:
None

Returns:
None

Example Usage:
To run the program, simply call the main() function.

"""


def main() -> None:
    listening_port = retrieve_port()
    logger = get_logger()
    config = ConfigWrapper(logger, "general_config")
    executor = ThreadPoolExecutor(max_workers=config.get_max_thread_load())
    loop_server(logger, config, listening_port, executor)


"""
Function: retrieve_port() -> int

Description:
This function prompts the user to enter a port number and returns it if it is a valid port number. 
If the port number is not valid, the function recursively calls itself until a valid port number is entered.

Parameters:
None

Returns:
An integer representing the port number entered by the user.

Example Usage:
To obtain a valid port number from the user, call the function like this: retrieve_port()

"""


def retrieve_port() -> int:
    try:
        my_port = int(input("Enter a port number (non-privileged ports are > 1023): "))
        if my_port > 1023:
            return my_port

        else:
            print("Port number must be greater than 1023.")
            return retrieve_port()
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        return retrieve_port()


"""
Function: loop_server(logger: BoundLogger, config: ConfigWrapper, port: int, executor: ThreadPoolExecutor) -> None

Description:
This function sets up a socket on the specified port and listens for incoming connections. 
When a client connects, it receives the incoming data, unpacks it, and checks the command type. 
If the command is "HELO", the function submits a new thread in the thread pool to handle the HELO request. 
If the command is not "HELO", the function logs the error message "Invalid command: {command}".

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve the server's host name, maximum package size, and other settings.
- port (int): The port number to listen on for incoming connections.
- executor (ThreadPoolExecutor): A thread pool executor to manage multiple threads.

Returns:
None

Example Usage:
To start the server listening on port 12345, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
loop_server(logger, config, 12345, executor)

"""


def loop_server(logger: BoundLogger, config: ConfigWrapper, port: int, executor: ThreadPoolExecutor) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as smtp_socket:
        smtp_socket.bind((config.get_host(), port))
        smtp_socket.listen()
        try:
            while True:
                conn, addr = smtp_socket.accept()
                logger.info(f"{addr} Service Ready")
                data = conn.recv(config.get_max_size_package_tcp())
                tuple_data = pickle.loads(data)
                command = tuple_data[0]
                data = tuple_data[1]
                if command == "HELO":
                    executor.submit(handle_helo, logger, config, data, conn, executor)
                else:
                    logger.info(f"Invalid command: {command}")

        except ConnectionResetError:
            # client has closed the connection unexpectedly
            logger.exception("Client closed the connection unexpectedly")
        except socket.timeout:
            # no data received within timeout period
            logger.exception("No data received from client within timeout period")
        except KeyboardInterrupt:
            # user has interrupted the program execution
            logger.info("Program interrupted by user")
        except ValueError:
            # data received cannot be converted to string
            logger.exception("Received data cannot be converted to string")
        except Exception as e:
            # any other exception
            logger.exception(f"An error occurred: {e}")


"""
Function: handle_helo(logger: BoundLogger, config: ConfigWrapper, message: str, connection: socket, executor: ThreadPoolExecutor) -> None

Description:
This function handles the "HELO" command for the SMTP server. 
It sends a greeting to the client and then submits a new thread in the thread pool to handle incoming email requests.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve server settings.
- message (str): The message associated with the "HELO" command (e.g. the client's domain name).
- connection (socket): The client's connection to the server.
- executor (ThreadPoolExecutor): A thread pool executor to manage multiple threads.

Returns:
None

Example Usage:
To handle the "HELO" command for the SMTP server, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
connection, address = smtp_socket.accept()
message = "example.com"
executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
handle_helo(logger, config, message, connection, executor)

"""


def handle_helo(logger: BoundLogger, config: ConfigWrapper, message: str, connection: socket,
                executor: ThreadPoolExecutor) -> None:
    SMTP_HELO(logger, config, "HELO", message, connection, executor)
    executor.submit(service_mail_request, logger, config, message, executor, connection)


"""
Function: service_mail_request(logger: BoundLogger, config: ConfigWrapper, data: str, executor: ThreadPoolExecutor, conn: socket) -> None

Description:
This function handles incoming email requests from clients. 
It receives incoming data, unpacks it, and calls the appropriate function to handle the SMTP command. 
It continues to handle incoming requests until the the connection is closed.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve server settings.
- data (str): The incoming data from the client.
- executor (ThreadPoolExecutor): A thread pool executor to manage multiple threads.
- conn (socket): The client's connection to the server.

Returns:
None

Example Usage:
To handle incoming email requests from clients, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
conn, address = smtp_socket.accept()
data = conn.recv(config.get_max_size_package_tcp())
executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
service_mail_request(logger, config, data, executor, conn)

"""


def service_mail_request(logger: BoundLogger, config: ConfigWrapper, data: str, executor: ThreadPoolExecutor,
                         conn: socket) -> None:
    with conn:
        while True:
            try:
                data = conn.recv(config.get_max_size_package_tcp())
                if not data:
                    logger.info("No data received, closing connection")
                    break
                tuple_data = pickle.loads(data)
                command = tuple_data[0]
                data = tuple_data[1]
                command_handler(logger, config, command, data, executor, conn)

            except ConnectionResetError:
                # client has closed the connection unexpectedly
                logger.exception("Client closed the connection unexpectedly")
                break
            except socket.timeout:
                # no data received within timeout period
                logger.exception("No data received from client within timeout period")
            except KeyboardInterrupt:
                # user has interrupted the program execution
                logger.info("Program interrupted by user")
                break
            except ValueError:
                # data received cannot be converted to string
                logger.exception("Received data cannot be converted to string")
            except Exception as e:
                # any other exception
                logger.exception(f"An error occurred: {e}")
                break


"""
Function: command_handler(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, executor: ThreadPoolExecutor, connection: socket) -> None

Description:
This function handles incoming SMTP commands from clients. 
It identifies the command being executed and calls the appropriate function to handle it.

Parameters:
- logger (BoundLogger): A logging object used to log events and errors.
- config (ConfigWrapper): A configuration object used to retrieve server settings.
- command (str): The SMTP command being executed (e.g. "HELO", "MAIL FROM", "RCPT TO", "DATA", etc.).
- message (str): The message associated with the SMTP command (e.g. the email address of the sender or recipient, the message to be sent, etc.).
- executor (ThreadPoolExecutor): A thread pool executor to manage multiple threads.
- connection (socket): The client's connection to the server.

Returns:
None

Example Usage:
To handle incoming SMTP commands from clients, call the function like this:
logger = get_logger()
config = ConfigWrapper(logger, "general_config")
connection, address = smtp_socket.accept()
command = "MAIL FROM"
message = "johndoe@example.com"
executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
command_handler(logger, config, command, message, executor, connection)

"""


def command_handler(logger: BoundLogger, config: ConfigWrapper, command: str, message: str,
                    executor: ThreadPoolExecutor, connection: socket) -> None:
    if command == "HELO":
        SMTP_HELO(logger, config, command, message, connection, executor)
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


def SMTP_HELO(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket,
              executor: ThreadPoolExecutor) -> None:
    logger.info(command + message)
    send_message = tuple("250 OK", "Hello " + message + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
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
    logger.info(command + message)
    send_message = tuple("250", " " + message + "... Sender ok" + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
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
    logger.info(command + message)
    send_message = tuple("250", " " + " root... Recipient ok" + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
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
    logger.info(command)
    logger.info("354 Enter Mail, end with '.' on a line by itself")
    write_to_mailbox(logger, config, message, mailbox_semaphore)
    send_message = tuple("250", " OK message accepted for delivery" + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
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
    logger.info(command)
    send_message = tuple("221", message + " Closing Connection" + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
    connection.sendall(pickle_data)
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
                     file_semaphore: threading.Semaphore) -> None:
    username = message.getToUsername()

    file_semaphore.acquire()
    mailbox_file = os.path.join("USERS", username, "my_mailbox.txt")

    with open(mailbox_file, 'a') as file:
        file.write(str(message) + '\n')
        file.flush()

    file_semaphore.release()


if __name__ == "__main__":
    main()
