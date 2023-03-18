from typing import Union
import hashlib
from structlog import BoundLogger

"""
Function: hash_string(password: str) -> str

Description:
This function takes a string input and returns its hash value using the SHA-256 algorithm. 
The hash value is returned as a string of hexadecimal digits.

Parameters:
- password: A string to be hashed.

Returns:
A string of hexadecimal digits representing the hash value of the input string.

Example Usage:
To hash a password string, call the function like this: hash_string("mypassword")
"""
def hash_string(password: str) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password.encode())
    return sha256_hash.hexdigest()

"""
Function: retrieve_command_promt_input(message_to_display: str, cast_to_int: bool = False, hash_input: bool = False) -> Union[str, int]

Description:
This function prompts the user for input using the command prompt and returns the input as a string or integer. 
It also has the option to cast the input to an integer and hash the input using the `hash_string()` function. 
If an error occurs during input processing, an error message is printed.

Parameters:
- message_to_display: A string message to be displayed to the user to prompt input.
- cast_to_int (optional): A boolean flag indicating whether the input should be cast to an integer (default: False).
- hash_input (optional): A boolean flag indicating whether the input should be hashed using the `hash_string()` function (default: False).

Returns:
A string or integer value representing the user input.

Example Usage:
To retrieve a string input from the user, call the function like this: retrieve_command_promt_input("Enter your name: ")
To retrieve an integer input from the user, call the function like this: retrieve_command_promt_input("Enter your age: ", cast_to_int=True)
To hash the input and retrieve the hashed value, call the function like this: retrieve_command_promt_input("Enter your password: ", hash_input=True)

"""
def retrieve_command_promt_input(message_to_display:str, logger: BoundLogger, cast_to_int: bool = False, hash_input: bool = False, port: bool= False) -> Union[str,int]:
    try:
        if port:
            command_prompt_input = retrieve_port(message_to_display, logger)
            return command_prompt_input
        command_prompt_input = input(message_to_display)
        if cast_to_int:
            command_prompt_input = int(command_prompt_input)
        if hash_input:
            if command_prompt_input == "quit":
                return "quit"
            command_prompt_input = hash_string(command_prompt_input)
        return command_prompt_input
    except Exception as e:
            logger.error(f"Error: {e}") 


def retrieve_port(message_to_display:str, logger: BoundLogger) -> int:
    try:
        my_port = int(input(message_to_display + " (non-privileged ports are > 1023): "))
        if my_port > 1023:
            return my_port
        
        else:
            logger.error(f"Error: port number must be > 1023")
            return retrieve_port(message_to_display, logger)
    except ValueError as e:
        logger.error(f"Error: {e}")
        return retrieve_port(message_to_display, logger)


"""
Function: get_parameters_mail_client()

Description:
This function prompts the user to enter the required parameters for configuring a mail client. Including:
- the server IP address
- SMTP server port 
- POP3 server port
- username

Parameters:
None

Returns:
A tuple of five elements. Including: 
- the server IP address (a string or integer)
- SMTP server port (an integer) 
- POP3 server port (an integer)
- username (a string or integer) 

Example Usage:
server_ip, SMTP_server_port, POP3_server_port, username = get_parameters_mail_client()

"""
def get_parameters_mail_client(logger: BoundLogger) -> tuple[str | int, str | int, str | int, str | int]:
    server_ip = retrieve_command_promt_input("Give IP address to connect to: ", logger)
    SMTP_server_port = retrieve_command_promt_input("Give SMTP server port",logger, cast_to_int=True, port=True)
    POP3_server_port = retrieve_command_promt_input("Give pop3 server port",logger, cast_to_int=True, port=True)
    username = retrieve_command_promt_input("Provide full mail account: ", logger)
    
    return server_ip, SMTP_server_port, POP3_server_port, username

