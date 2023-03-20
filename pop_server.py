import socket
import threading
import pickle
import os
from typing import Union

from structlog import get_logger, BoundLogger
from helper_files.ConfigWrapper import ConfigWrapper

# define a semaphore so only 1 thread can access the mailbox.
mailbox_semaphore = threading.Semaphore(1)
thread_local = threading.local()


def main() -> None:
    logger = get_logger()
    logger.info("Starting POP3 Server")
    try:
        listening_port = retrieve_port(logger)
        config = ConfigWrapper(logger,"general_config")
        loop_server(logger, config, listening_port)
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        pass
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        pass


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
        pass
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        pass


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
                pass
            except socket.timeout:
                # no data received within timeout period
                logger.exception("No data received from client within timeout period")
                pass
            except KeyboardInterrupt:
                # user has interrupted the program execution
                logger.info("Program interrupted by user")
                pass
            except ValueError:
                # data received cannot be converted to string
                logger.exception("Received data cannot be converted to string")
                pass
            except Exception as e:
                # any other exception
                logger.exception(f"An error occurred: {e}")
                pass
            

def handle_client(logger: BoundLogger, config: ConfigWrapper, conn: socket.socket) -> None:
    thread_id = threading.get_ident()
    logger.info(f"Thread {thread_id} started")
    global thread_local
    thread_local.server_state = "AUTHORIZATION"
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
            command_handler(logger, config, command, data, conn)
        
    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        conn.sendall(pickle_data)
        pass
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        conn.sendall(pickle_data)
        pass


def command_handler(logger: BoundLogger, config: ConfigWrapper, command: str, message: Union[str,int], connection: socket) -> None:
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


def pop3_PASS(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    logger.info(command + message)
    passwords = set()
    with open('userinfo.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split()
            passwords.add(password)
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


        mailbox_file = os.path.join("USERS", thread_local.session_username, "my_mailbox.txt")
        mailbox_file.strip()
        with open(mailbox_file, 'r') as f:
            mailbox = f.readlines()

        updated_mailbox = [line for line in mailbox if not line.startswith('X')]
        if len(mailbox) != len(updated_mailbox):
            try:
                mailbox_semaphore.acquire()
                with open(mailbox_file, 'w') as f:
                    f.writelines(updated_mailbox)
            finally:
                mailbox_semaphore.release()
        send_message = ("+OK", " Thanks for using POP3 server")
        pickle_data = pickle.dumps(send_message)
        logger.info(send_message[0] + send_message[1])
        connection.sendall(pickle_data)


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

def pop3_LIST(logger: BoundLogger, config: ConfigWrapper, command: str, message: int, connection: socket) -> None:
    global thread_local
    logger.info(command + str(message))
    mailbox_file = os.path.join("USERS", thread_local.session_username, "my_mailbox.txt")
    mailbox_file.strip()
    with open(mailbox_file, 'r') as f:
        mailbox = f.readlines()

    non_deleted_mailbox = get_not_deleted_messages(mailbox)
    number_of_messages = len(non_deleted_mailbox)
    total_size_mailbox = 0
    message_size_list = []
    for scan_listing in non_deleted_mailbox:
        bytes = scan_listing.encode('utf-8')
        size = len(bytes)
        message_size_list.append(size)
        total_size_mailbox += size

    if message == '' or message == None or message == " ":
        send_message = ("+OK", f" {number_of_messages} messages  ({total_size_mailbox} octets)" + "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
        for scan_listing in range(1, number_of_messages):
            send_message = ("+OK", f" {scan_listing} {message_size_list[scan_listing-1]}" + "\r\n")
            pickle_data = pickle.dumps(send_message)
            connection.sendall(pickle_data)

        send_message = (".", " ")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    else:
        message_number = int(message)
        number_of_messages = len(non_deleted_mailbox)
        if message_number > number_of_messages:
            send_message = ("-ERR", f" No such message, only {number_of_messages} in maildrop" + "\r\n")
            pickle_data = pickle.dumps(send_message)
            connection.sendall(pickle_data)
        else:
            send_message = ("+OK", f"{message_number}   {message_size_list[message_number - 1]}" + "\r\n")
            pickle_data = pickle.dumps(send_message)
            connection.sendall(pickle_data)

            for scan_listing in range(1, number_of_messages+1):
                send_message = ("+OK", f" {scan_listing} {message_size_list[scan_listing-1]}" + "\r\n")
                pickle_data = pickle.dumps(send_message)
                connection.sendall(pickle_data)


            send_message = (".", str(" ") )
            pickle_data = pickle.dumps(send_message)
            connection.sendall(pickle_data)


def pop3_RETR(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    try:
        logger.info(command + message)
        requested_message_number = int(message.strip())
        mailbox_file = os.path.join("USERS", thread_local.session_username, "my_mailbox.txt")
        mailbox_file.strip()
        with open(mailbox_file, 'r') as f:
            mailbox = f.readlines()

        non_deleted_mailbox = get_not_deleted_messages(mailbox)
        requested_message = non_deleted_mailbox[requested_message_number-1]
        requested_message_size = len(requested_message.encode('utf-8'))

        
        send_message = ("+OK", f" {requested_message_size} octets" + "\r\n")
        logger.debug(f"{send_message[0]}   {send_message[1]}")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)

        
        send_message = (requested_message_number, f" {requested_message}" + "\r\n")
        pickle_data = pickle.dumps(send_message)
        logger.debug(f"{send_message[0]}   {send_message[1]}")
        connection.sendall(pickle_data)

    except KeyboardInterrupt:
        logger.exception("Program interrupted by user")
        send_message = ("554", "The server was interrupted by the server owner"+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
        pass
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        send_message = ("554", f"The server was terminated because an error occurred. Error: {e} "+ "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
        pass


def pop3_DELE(logger: BoundLogger, config: ConfigWrapper, command: str, message: str, connection: socket) -> None:
    global thread_local
    try:
        logger.info(command + message)
        requested_message_number = int(message.strip())
        mailbox_file = os.path.join("USERS", thread_local.session_username, "my_mailbox.txt")
        mailbox_file.strip()
        with open(mailbox_file, 'r') as f:
            mailbox = f.readlines()
        index_messages_in_file = [index for index, value in enumerate(mailbox) if value.startswith('From: ')]
        index_of_message_to_delete_in_file = index_messages_in_file[requested_message_number -1]

        index_of_next_message_in_file = index_messages_in_file[requested_message_number]
        mailbox[index_of_message_to_delete_in_file: index_of_next_message_in_file] = ['X' + line for line in mailbox[index_of_message_to_delete_in_file: index_of_next_message_in_file]]
        logger.info(f"Marked message {requested_message_number} for deletion")
        mailbox_semaphore.acquire()
        with open(mailbox_file, 'w') as f:
            f.writelines(mailbox)
        send_message = ("+OK", f" message {requested_message_number} deleted" + "\r\n")
        pickle_data = pickle.dumps(send_message)
        connection.sendall(pickle_data)
    except Exception as e:
        raise e
    finally:
        mailbox_semaphore.release()


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

#insert the non-formatted mailbox
def get_not_deleted_messages(mailbox: list[str]) -> list[str]:
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

    return updated_mailbox
    


if __name__ == "__main__":
    main()