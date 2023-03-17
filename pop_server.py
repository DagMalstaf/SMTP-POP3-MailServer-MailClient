import socket
import threading
import pickle
import os

from concurrent.futures import ThreadPoolExecutor
from structlog import get_logger, BoundLogger
from helper_files.ConfigWrapper import ConfigWrapper

# define a semaphore so only 1 thread can access the mailbox.
mailbox_semaphore = threading.Semaphore(1)



def main() -> None:
    listening_port = retrieve_port()
    logger = get_logger()
    config = ConfigWrapper(logger,"general_config")
    executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
    server_state = "READY"
    session_username = str()
    loop_server(logger, config, listening_port, executor, server_state, session_username)


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



def loop_server(logger: BoundLogger, config: ConfigWrapper, port: int, executor: ThreadPoolExecutor, server_state: str, session_username:str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pop3_socket:
        pop3_socket.bind((config.get_host(), port))
        pop3_socket.listen()
        try:
            while True:
                conn, addr = pop3_socket.accept()
                conn.send("+OK POP3 server ready")
                logger.info(f"{addr} Service Ready")
                server_state = "AUTHORIZATION"
                logger.info(f"Server is now in the {server_state} STATE")
                data = conn.recv(config.get_max_size_package_tcp())
                tuple_data = pickle.loads(data)
                command = tuple_data[0]
                data = tuple_data[1]
                if command == "USER ":
                    executor.submit(handle_user, logger, config, data, conn, executor, server_state, session_username)
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
            

def handle_user(logger: BoundLogger, config: ConfigWrapper, message: str, connection: socket, executor: ThreadPoolExecutor, server_state: str, session_username: str) -> None:
    if pop3_USER(logger, config, "USER ", message, connection, executor, session_username):
        executor.submit(service_mail_request, logger, config, message, executor, connection, server_state, session_username)



def service_mail_request(logger: BoundLogger, config: ConfigWrapper, data: str, executor: ThreadPoolExecutor, conn: socket, server_state: str, session_username: str) -> None:
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
                command_handler(logger, config, command, data, executor, conn, server_state, session_username)

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


def command_handler(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, executor: ThreadPoolExecutor, connection: socket, server_state: str, session_username: str) -> None:
    if command == "USER ":
        pop3_USER(logger, config, command,  message, connection, executor, session_username)
    elif command == "PASS ":
        pop3_PASS(logger, config, command, message, connection, server_state)
    elif command == "QUIT":
        pop3_QUIT(logger, config, command, message, connection, server_state, session_username)
    elif command == "STAT":
        pop3_STAT(logger, config, command, message, connection, session_username)
    elif command == "LIST":
        pop3_LIST(logger, config, command, message, connection)
    elif command == "RETR":
        pop3_RETR(logger, config, command, message, connection)
    elif command == "DELE":
        pop3_DELE(logger, config, command, message, connection)
    else:
        logger.info(f"Invalid command: {command}")


def pop3_USER(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket, executor: ThreadPoolExecutor, session_username:str) -> bool:
    logger.info(command + message)
    usernames = set()
    with open('userinfo.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split()
            usernames.add(username)
    try:
        if message in usernames:
            send_message = tuple("+OK", " User accepted")
            session_username = message
            logger.info(f"Session username: {session_username}")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
            return True
        else:
            send_message = tuple("-ERR", " [AUTH] Invalid username")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
            return False
    except Exception as e:        
        logger.exception(f"An error occurred: {e}")
        send_message = tuple("-ERR", " [AUTH] Authentication failed due to server error")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
        return False


def pop3_PASS(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket, executor: ThreadPoolExecutor, server_state: str) -> None:
    logger.info(command + message)
    passwords = set()
    with open('userinfo.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split()
            passwords.add(password)
    try:
        if message in passwords:
            send_message = tuple("+OK", " Password accepted")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            server_state = "TRANSACTION"
            logger.info(f"Server is now in the {server_state} STATE")
            connection.sendall(pickle_data)
        else:
            send_message = tuple("-ERR", " [AUTH] Invalid password")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
    except Exception as e:        
        logger.exception(f"An error occurred: {e}")
        send_message = tuple("-ERR", " [AUTH] Authentication failed due to server error")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)


def pop3_QUIT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket, server_state: str, session_username: str) -> None:
    if server_state == "AUTHORIZATION":
        logger.info(command + message)
        logger.info("Client terminated the connection in the AUTHORIZATION STATE")
        logger.info("Server is now terminating the connection")
        send_message = tuple("+OK", " Thanks for using POP3 server")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
        try:
            connection.close()
        except Exception as e:
            logger.exception(f"An error occurred while closing the connection: {e}")
    
    elif server_state == "TRANSACTION":
        logger.info(command + message)
        server_state = "UPDATE"
        logger.info(f"Server is now in the {server_state} STATE")
        send_message = tuple("-ERR", " [AUTH] Authentication or connection failed due to server error")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        logger.info("Server will now clean up all resources and close the connection")

        mailbox_semaphore.acquire()
        try:
            mailbox_file = os.path.join("USERS", session_username, "my_mailbox.txt")
            with open(mailbox_file, 'r') as f:
                mailbox = f.readlines()
            
            formatted_mailbox = get_messages_list(mailbox)
            deleted_messages = []
            updated_mailbox = []
            for index, message in enumerate(formatted_mailbox):
                if message.startswith('X'):
                    deleted_messages.append(index)
                else:
                    updated_mailbox.append(message)
            for index in reversed(deleted_messages):
                del updated_mailbox[index]
            
            with open(mailbox_file, 'w') as f:
                f.writelines(updated_mailbox)
        except Exception as e:
            logger.exception(f"An error occurred while closing the connection: {e}")
        finally:
            mailbox_semaphore.release() 
            
        try:
            connection.close()
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
        finally:
            connection.sendall(pickle_data)
    

def pop3_STAT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket, session_username: str) -> None:
    logger.info(command + message)
    mailbox_file = os.path.join("USERS", session_username, "my_mailbox.txt")
    with open(mailbox_file, 'r') as f:
        mailbox = f.readlines()
    formatted_mailbox = get_messages_list(mailbox)
    number_of_messages = len(formatted_mailbox)
    total_size_mailbox = 0
    for message in formatted_mailbox:
        bytes = message.encode('utf-8')
        total_size_mailbox += len(bytes)
    if number_of_messages >= 0 and total_size_mailbox >= 0:
        send_message = tuple("+OK", " " + str(number_of_messages) + " " + str(total_size_mailbox))
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)

def pop3_LIST(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    pass

def pop3_RETR(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    pass

def pop3_DELE(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    pass


def get_messages_list(mailbox: list[str]) -> list[str]:
    messages = []
    current_message = ""
    for line in mailbox:
        if line.strip() == "":
            if current_message != "":
                messages.append(current_message.strip())
                current_message = ""
        else:
            current_message += line
    if current_message != "":
        messages.append(current_message.strip())


if __name__ == "__main__":
    main()