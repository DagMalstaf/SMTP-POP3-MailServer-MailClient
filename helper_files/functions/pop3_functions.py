import socket
import pickle
from typing import List
from structlog import BoundLogger

from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.functions.general_helper_functions import retrieve_command_promt_input
from helper_files.ConfigWrapper import ConfigWrapper

def pop3_authentication(self, connection) -> bool:
        try:
            while True:
                user_authentication_response = pop3_USER(self._logger, self._config, connection, self._username)
                if not user_authentication_response:
                    self._logger.error("User authentication failed")
                    self._username = retrieve_command_promt_input("Please enter your correct username or 'quit' to terminate : ", self._logger,)
                    if self._username == "quit":
                        return False
                    
                else:
                    self._logger.info("User authentication successful")
                    self._password = retrieve_command_promt_input("Provide password of mail account or 'quit' to terminate : ", self._logger, hash_input=False)
                    if self._password == "quit":
                        return False
                    else:
                        pass_authentication_response = pop3_PASS(self._logger, self._config, connection, self._password)
                        if not pass_authentication_response:
                            self._logger.error("Password authentication failed")
                            self._password = retrieve_command_promt_input("Please enter your correct password or 'quit' to terminate : ", self._logger,)
                            if self._password == "quit":
                                return False
                            
                        else:
                            self._logger.info("Password authentication successful")
                            return True
        except Exception as e:
            self._logger.exception(f"An error occurred: {e}")
            return False


def pop3_USER(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket, username: str) -> bool:
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
    

def pop3_PASS(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket, password: str) -> bool:
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
        logger.error(f"Recieved response code: {response_code} from POP3 server")

    

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
    else:
        recieving = True
        logger.info(tuple_data[1])
        while recieving:
            response_message_for_list = pop3_socket.recv(config.get_max_size_package_tcp())
            tuple_data = pickle.loads(response_message_for_list)
            response_code = tuple_data[0]
            message = tuple_data[1]
            logger.info(message)
            if response_code == ".":
                recieving = False
                return
            
        
    

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
        logger.debug(f"this is the code: {response_code}, and this is the message: {message}")
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



