import socket
import pickle
from typing import List
from structlog import BoundLogger

from helper_files.functions.general_helper_functions import retrieve_command_promt_input
from helper_files.ConfigWrapper import ConfigWrapper
from helper_files.MessageWrapper import MessageWrapper

def pop3_authentication(self, connection) -> bool:
        try:
            while True:
                user_authentication_response = pop3_USER(self._logger, self._config, connection, self._username)
                if not user_authentication_response:
                    self._logger.info("User authentication failed")
                    self._username = retrieve_command_promt_input("Please enter your correct username or 'quit' to terminate : ")
                    if self._username == "quit":
                        return False
                    continue
                else:
                    self._logger.info("User authentication successful")
                    self._password = retrieve_command_promt_input("Provide password of mail account or 'quit' to terminate : ", hash_input=True)
                    if self._password == "quit":
                        return False
                    else:
                        pass_authentication_response = pop3_PASS(self._logger, self._config, connection, self._password)
                        if not pass_authentication_response:
                            self._logger.info("Password authentication failed")
                            self._password = retrieve_command_promt_input("Please enter your correct password or 'quit' to terminate : ")
                            if self._password == "quit":
                                return False
                            continue
                        else:
                            self._logger.info("Password authentication successful")
                            return True
        except Exception as e:
            self._logger.exception(f"An error occurred: {e}")
            return False


def pop3_USER(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket, username: str) -> bool:
    send_message = tuple("USER ", username)
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)

    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "-ERR":
        logger.error(response_code + tuple_data[1])
        return False
    else:
        logger.info(response_code + tuple_data[1])
        return True
    

def pop3_PASS(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket, password: str) -> bool:
    send_message = tuple("PASS ", password)
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)

    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "-ERR":
        logger.error(response_code + tuple_data[1])
        return False
    else:
        logger.info(response_code + tuple_data[1])
        return True
    

def pop3_QUIT(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket) -> None:
    send_message = tuple("Quit ", " Request to terminate the connection to the pop3 server")
    pickle_data = pickle.dumps(send_message)
    pop3_socket.sendall(pickle_data)


    response_message = pop3_socket.recv(config.get_max_size_package_tcp())
    tuple_data = pickle.loads(response_message)
    response_code = tuple_data[0]
    if response_code == "-ERR":
        logger.error(response_code + tuple_data[1])
        return False
    else:
        logger.info(response_code + tuple_data[1])
        return True
    pass

def pop3_STAT(logger: BoundLogger, config: ConfigWrapper, pop3_socket: socket) -> None:
    pass

def pop3_LIST(**kwargs) -> None:
    pass

def pop3_RETR(**kwargs) -> None:
    pass

def pop3_DELE(**kwargs) -> None:
    pass




















# https://www.geeksforgeeks.org/args-kwargs-python/
# see MailManagement
def pop3_authentication(**kwargs) -> bool:
    username = kwargs.get("username")
    password = kwargs.get("password")
    return True
    #TODO: authentication is done on pop3 server
    #TODO: sending username and hashed password to pop3 server
    #TODO: return bool to signal successful authentication

    #TODO: IMPORTANT: ask for information on mail management on the establishment of a connection to pop3 sever
    #TODO: after authentication, but we have to send credentials to authenticate ?????

