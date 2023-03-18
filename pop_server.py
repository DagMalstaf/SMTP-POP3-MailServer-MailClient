import socket
import threading
import pickle
import os

from concurrent.futures import ThreadPoolExecutor
from structlog import get_logger, BoundLogger
from helper_files.ConfigWrapper import ConfigWrapper

# define a semaphore so only 1 thread can access the mailbox.
mailbox_semaphore = threading.Semaphore(1)
thread_local = threading.local()



def main() -> None:
    try:
        logger = get_logger()
        logger.info("Starting POP3 Server")
        listening_port = retrieve_port(logger)
        config = ConfigWrapper(logger,"general_config")
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as pop3_socket:
        pop3_socket.bind((config.get_host(), port))
        pop3_socket.listen()
        logger.info(f"Listening on port {port}")
        while True:
            try:
                conn, addr = pop3_socket.accept()
                logger.info(f"{addr} Client connected")
                conn.send(("+OK POP3 server ready").encode())
                thread = threading.Thread(target=handle_client, args= (logger, config, conn))
                thread.start()
                
            
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
            

def handle_client(logger: BoundLogger, config: ConfigWrapper, conn: socket.socket) -> None:
    thread_id = threading.get_ident()
    logger.info(f"Thread {thread_id} started")
    global thread_local
    thread_local.server_state = str("AUTHORIZATION")
    thread_local.session_username = str()
    thread_local.user_authenticated = False
    try:
        logger.info(f"Server is now in the {thread_local.server_state} STATE")
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
                pop3_QUIT(logger, config, command, data, conn)
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



def command_handler(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    if command == "USER " and thread_local.server_state == "AUTHORIZATION":
        thread_local.user_authenticated = pop3_USER(logger, config, command,  message, connection)

    elif command == "PASS " and thread_local.server_state == "AUTHORIZATION" and thread_local.user_authenticated:
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


def pop3_USER(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> bool:
    global thread_local
    logger.info(command + message)
    usernames = set()
    with open('userinfo.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split()
            usernames.add(username)
    try:
        if message in usernames:
            send_message = ("+OK", " User accepted")
            thread_local.session_username = message
            logger.info(f"Session username: {thread_local.session_username}")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
            return True
        else:
            send_message = ("-ERR", " [AUTH] Invalid username")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
            return False
    except Exception as e:        
        logger.exception(f"An error occurred: {e}")
        send_message = ("-ERR", " [AUTH] Authentication failed due to server error")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
        return False


def pop3_PASS(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    logger.info(command + message)
    passwords = set()
    with open('userinfo.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split()
            passwords.add(password)
    try:
        if message in passwords:
            send_message = ("+OK", " Password accepted")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            thread_local.server_state = str("TRANSACTION")
            logger.info(f"Server is now in the {thread_local.server_state} STATE")
            connection.sendall(pickle_data)
        else:
            send_message = ("-ERR", " [AUTH] Invalid password")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
    except Exception as e:        
        logger.exception(f"An error occurred: {e}")
        send_message = ("-ERR", " [AUTH] Authentication failed due to server error")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)


def pop3_QUIT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    if thread_local.server_state == "AUTHORIZATION":
        logger.info(command + message)
        logger.info("Client terminated the connection in the AUTHORIZATION STATE")
        logger.info("Server is now terminating the connection")
        send_message = ("+OK", " Thanks for using POP3 server")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)
        
    
    elif thread_local.server_state == "TRANSACTION":
        logger.info(command + message)
        thread_local.server_state = str("UPDATE")
        logger.info(f"Server is now in the {thread_local.server_state} STATE")
        logger.info("Server will now clean up all resources and close the connection")

        mailbox_semaphore.acquire()
        try:
            mailbox_file = os.path.join("USERS", thread_local.session_username, "my_mailbox.txt")
            mailbox_file.strip()
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
            send_message = ("+OK", " Thanks for using POP3 server")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
            
        except Exception as e:
            logger.exception(f"An error occurred while closing the connection: {e}")
            send_message = ("-ERR", " [AUTH] Authentication failed due to server error")
            pickle_data = pickle.dumps(send_message)
            logger.info(send_message[0] + send_message[1])
            connection.sendall(pickle_data)
        finally:
            mailbox_semaphore.release() 
            
            
    

def pop3_STAT(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    logger.info(command + message)
    mailbox_file = os.path.join("USERS", thread_local.session_username, "my_mailbox.txt")
    mailbox_file.strip()
    with open(mailbox_file, 'r') as f:
        mailbox = f.readlines()
    formatted_mailbox = get_messages_list(mailbox)
    number_of_messages = len(formatted_mailbox)
    total_size_mailbox = 0
    for message in formatted_mailbox:
        bytes = message.encode('utf-8')
        total_size_mailbox += len(bytes)
    if number_of_messages >= 0 and total_size_mailbox >= 0:
        send_message = ("+OK", " " + str(number_of_messages) + " " + str(total_size_mailbox)+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)

def pop3_LIST(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    pass

def pop3_RETR(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    pass

def pop3_DELE(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
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
    
    return messages


if __name__ == "__main__":
    main()