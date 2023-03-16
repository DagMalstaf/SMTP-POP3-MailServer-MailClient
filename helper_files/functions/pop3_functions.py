import socket
import pickle
from typing import List
from structlog import BoundLogger

from helper_files.ConfigWrapper import ConfigWrapper
from helper_files.MessageWrapper import MessageWrapper


def pop3_USER(logger: BoundLogger, config: ConfigWrapper, pop3_socket, username) -> bool:
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
    

def pop3_PASS(logger: BoundLogger, config: ConfigWrapper, pop3_socket, password) -> bool:
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
    

def pop3_QUIT() -> None:
    pass

def pop3_STAT() -> None:
    pass

def pop3_LIST() -> None:
    pass

def pop3_RETR() -> None:
    pass

def pop3_DELE() -> None:
    pass

def pop3_count() -> None:
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

