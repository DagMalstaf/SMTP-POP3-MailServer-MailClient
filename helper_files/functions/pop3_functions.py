import socket
import pickle
from structlog import BoundLogger

from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.functions.general_helper_functions import retrieve_command_promt_input
from helper_files.ConfigWrapper import ConfigWrapper


def pop3_authentication(logger: BoundLogger, config: ConfigWrapper, username: str, connection: socket) -> bool:
    try:
        while True:
            user_authentication_response = __pop3_USER(logger, config, connection, username)
            if not user_authentication_response:
                logger.error("User authentication failed")
                username = retrieve_command_promt_input("Please enter your correct username or 'quit' to terminate : ", logger,)
                if username == "quit":
                    return False
            else:
                logger.info("User authentication successful")
                password = retrieve_command_promt_input("Provide password of mail account or 'quit' to terminate : ", logger, hash_input=True)
                if password == "quit":
                    return False
                pass_authentication_response = __pop3_PASS(logger, config, connection, password)
                if pass_authentication_response:
                    logger.info("Password authentication successful")
                    return True
                else:
                    logger.error("Password authentication failed")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return False
        pass


def __pop3_USER(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket, username: str) -> bool:

    send_message = ("USER ", username)
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)

    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "-ERR":
        logger.error(response_code + tuple_data[1])
        return False
    else:
        return True
    

def __pop3_PASS(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket, password: str) -> bool:
    send_message = ("PASS ", password)
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)

    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "-ERR":
        logger.error(response_code + tuple_data[1])
        return False
    else:
        return True
    

def pop3_QUIT(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket) -> None:
    send_message = ("QUIT", " Request to terminate the connection to the pop3 server")
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)

    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "+OK":
        logger.info(response_code + tuple_data[1])
        pop3_socket.close()
        raise RestartMailServerError()
    else:
        logger.error(f"Recieved response code: {response_code} from POP3 server")
        raise RestartMailServerError

def pop3_STAT(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket) -> None:
    send_message = ("STAT", " Request to retrieve information from the mailbox")
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)

    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "+OK":
        logger.info(tuple_data[1])
    else:
        logger.error(f"Received response code: {response_code} from POP3 server")
        pop3_socket.close()
        raise RestartMailServerError

    

def pop3_LIST(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket) -> None:
    logger.info("Please provide the message number you want to list.\n If you don't enter a number all messages will be listed.")
    message_number = retrieve_command_promt_input("Message number: ", logger)
    send_message = ("LIST", message_number)
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)
    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "-ERR":
        logger.error(f"Recieved response code: {response_code} from POP3 server")
        logger.error(f"Recieved message: {tuple_data[1]} from POP3 server")
        pop3_socket.close()
        raise RestartMailServerError
    else:
        logger.info(tuple_data[1])
        while response_code != ".":
            response_message_for_list = pop3_socket.recv(config.get_max_size_package_tcp())
            tuple_data = pickle.loads(response_message_for_list)
            response_code = tuple_data[0]
            message = tuple_data[1]
            logger.info(message)

            logger.debug(f"Recieved response code: {response_code} from POP3 server")
            logger.debug(f"Recieved message: {tuple_data[1]} from POP3 server")
            

def pop3_RETR(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket) -> None:
    logger.info("Please provide the message number you want to retrieve.\n")
    message_number = retrieve_command_promt_input("Message number: ", logger)
    send_message = ("RETR", message_number)
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)
    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "+OK":
        logger.info(tuple_data[1])
        response_message_for_retr = pop3_socket.recv(config.get_max_size_package_tcp())
        tuple_data = pickle.loads(response_message_for_retr)
        response_code = tuple_data[0]
        message = tuple_data[1]
        if int(response_code) == int(message_number):
            logger.info(message)
        else:
            logger.error(f"Recieved the message number: {response_code}, but expected {message_number}")

    else:
        logger.error(f"Recieved response code: {response_code} from POP3 server")
        logger.error(f"Recieved message: {tuple_data[1]} from POP3 server")


def pop3_DELE(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket) -> None:
    logger.info("Please provide the message number you want to delete.\n")
    message_number = retrieve_command_promt_input("Message number: ", logger)
    send_message = ("DELE", message_number)
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)
    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "+OK":
        logger.info(tuple_data[1])
    
    else:
        logger.error(f"Recieved response code: {response_code} from POP3 server")
        logger.error(f"Recieved message: {tuple_data[1]} from POP3 server")




