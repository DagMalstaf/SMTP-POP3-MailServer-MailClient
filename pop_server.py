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
    listening_port = retrieve_port()
    logger = get_logger()
    config = ConfigWrapper(logger,"general_config")
    executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
    loop_server(logger, config, listening_port, executor)


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



def loop_server(logger: BoundLogger, config: ConfigWrapper, port: int, executor: ThreadPoolExecutor) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pop3_socket:
        pop3_socket.bind((config.get_host(), port))
        pop3_socket.listen()
        try:
            while True:
                conn, addr = pop3_socket.accept()
                conn.send("+OK POP3 server ready")
                logger.info(f"{addr} Service Ready")
                data = conn.recv(config.get_max_size_package_tcp())
                tuple_data = pickle.loads(data)
                command = tuple_data[0]
                data = tuple_data[1]
                if command == "USER ":
                    executor.submit(handle_user, logger, config, data, conn, executor)
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
            

def handle_user(logger: BoundLogger, config: ConfigWrapper, message: str, connection: socket, executor: ThreadPoolExecutor) -> None:
    if pop3_USER(logger, config, "USER ", message, connection, executor):
        executor.submit(service_mail_request, logger, config, message, executor, connection)

            


def service_mail_request(logger: BoundLogger, config: ConfigWrapper, data: str, executor: ThreadPoolExecutor, conn: socket) -> None:
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


def command_handler(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, executor: ThreadPoolExecutor, connection: socket) -> None:
    if command == "USER ":
        pop3_USER(logger, config, command,  message, connection, executor)
    elif command == "PASS ":
        pop3_PASS(logger, config, command, message, connection)
    elif command == "QUIT":
        pop3_QUIT(logger, config, command, message, connection)
    elif command == "STAT":
        pop3_STAT(logger, config, command, message, connection)
    elif command == "LIST":
        pop3_LIST(logger, config, command, message, connection)
    elif command == "RETR":
        pop3_RETR(logger, config, command, message, connection)
    elif command == "DELE":
        pop3_DELE(logger, config, command, message, connection)
    else:
        logger.info(f"Invalid command: {command}")


def pop3_USER(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket, executor: ThreadPoolExecutor) -> None:
    logger.info(command + message)
    usernames = set()
    with open('userinfo.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split()
            usernames.add(username)
    try:
        if message in usernames:
            send_message = tuple("+OK", " User accepted")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
        else:
            send_message = tuple("-ERR", " [AUTH] Invalid username")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
    except Exception as e:        
        logger.exception(f"An error occurred: {e}")
        send_message = tuple("-ERR", " [AUTH] Authentication failed due to server error")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)


def pop3_PASS(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket, executor: ThreadPoolExecutor) -> None:
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



def pop3_QUIT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    logger.info(command + message)
    send_message = tuple("+OK", " Thanks for using POP3 server")
    """
    def pop3_QUIT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    logger.info(command + message)
    
    # 1. Delete any messages marked for deletion
    mailbox_semaphore.acquire()
    try:
        username = get_username_from_message(message)
        mailbox_file = os.path.join(username, 'my_mailbox.txt')
        
        with open(mailbox_file, 'r') as f:
            mailbox = f.readlines()
        
        deleted_messages = []
        updated_mailbox = []
        
        for i, msg in enumerate(mailbox):
            if msg.startswith('X'):
                deleted_messages.append(i)
            else:
                updated_mailbox.append(msg)
        
        # Remove deleted messages from the mailbox
        for i in reversed(deleted_messages):
            del updated_mailbox[i]
        
        # Rewrite the mailbox file without deleted messages
        with open(mailbox_file, 'w') as f:
            f.writelines(updated_mailbox)
    
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
    
    finally:
        mailbox_semaphore.release()
    
    # 2. Close any open files
    try:
        connection.close()
    
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
    
    send_message = tuple("+OK", " Thanks for using POP3 server")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
    connection.sendall(pickle_data)

    """
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
    connection.sendall(pickle_data)

def pop3_STAT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    logger.info(command + message)
    send_message = tuple("250", " " + " root... Recipient ok" + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
    connection.sendall(pickle_data)


def pop3_LIST(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    logger.info(command)
    logger.info("354 Enter Mail, end with '.' on a line by itself")
    write_to_mailbox(logger, config, message, mailbox_semaphore)
    send_message = tuple("250", " OK message accepted for delivery"  + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
    connection.sendall(pickle_data)
    

def pop3_RETR(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    logger.info(command)
    send_message = tuple("221", message + " Closing Connection" + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
    connection.sendall(pickle_data)
    

def pop3_DELE(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    logger.info(command)
    send_message = tuple("221", message + " Closing Connection" + "\r\n")
    pickle_data = pickle.dumps(send_message)
    logger.info(send_message[0] + send_message[1])
    connection.sendall(pickle_data)
    


def write_to_mailbox(logger: BoundLogger, config: ConfigWrapper, message: MessageWrapper, file_semaphore: threading.Semaphore) -> None:
    username = message.getToUsername()

    file_semaphore.acquire()
    with open(os.path.join(username, 'my_mailbox.txt'), 'a') as file:
        file.write(str(message) + '\n')
        file.flush()

    file_semaphore.release()
   

if __name__ == "__main__":
    main()