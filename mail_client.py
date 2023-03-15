from structlog import BoundLogger
from multiprocessing import get_logger
from typing import Union, Dict

from helper_files.Action import Action
from helper_files.ConfigWrapper import ConfigWrapper
import hashlib



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
def retrieve_command_promt_input(message_to_display:str, cast_to_int: bool = False, hash_input: bool = False) -> Union[str,int]:
    try:
        command_prompt_input = input(message_to_display)
        if cast_to_int:
            command_prompt_input = int(command_prompt_input)
        if hash_input:
            command_prompt_input = hash_string(command_prompt_input)
        return command_prompt_input
    except Exception as e:
            print(f"Error: {e}")


"""
Function: get_parameters_mail_client()

Description:
This function prompts the user to enter the required parameters for configuring a mail client. Including:
- the server IP address
- SMTP server port 
- POP3 server port
- username
- password. 
The username and password are also hashed for security reasons.

Parameters:
None

Returns:
A tuple of five elements. Including: 
- the server IP address (a string or integer)
- SMTP server port (an integer) 
- POP3 server port (an integer)
- username (a string or integer) 
- password (a string ).

Example Usage:
server_ip, SMTP_server_port, POP3_server_port, username, password = get_parameters_mail_client()

"""
def get_parameters_mail_client() -> tuple[str | int, str | int, str | int, str | int, str]:
    server_ip = retrieve_command_promt_input("Give IP address to connect to: ")
    SMTP_server_port = retrieve_command_promt_input("Give SMTP server port: ", cast_to_int=True)
    POP3_server_port = retrieve_command_promt_input("Give pop3 server port: ", cast_to_int=True)
    username = retrieve_command_promt_input("Provide username of mail account: ")
    password = retrieve_command_promt_input(" Provide password of mail account: ", hash_input=True)
    return server_ip, SMTP_server_port, POP3_server_port, username, password



"""
Function: main(logger: BoundLogger, config: ConfigWrapper)

Description:
This function is the main entry point for the mail client program. 
It prompts the user for the required parameters using the `get_parameters_mail_client()` function, 
and then enters a loop to perform mail client actions based on user input. 
It uses the `retrieve_command_promt_input()` function to prompt the user for input, 
and the `ConfigWrapper` class to obtain the available mail client actions and their corresponding classes. 

If an error occurs during action execution, it is caught and a generic error message is printed.


Parameters:
- logger: An instance of the `BoundLogger` class for logging events.
- config: An instance of the `ConfigWrapper` class for accessing configuration parameters.

Returns:
None

Example Usage:
To start the mail client program, call the function like this: main(logger, config)

"""
def main(logger: BoundLogger, config: ConfigWrapper ):
    ip_address,SMTP_port, POP3_port, username, password = get_parameters_mail_client()
    while True:
        try:
            action = retrieve_command_promt_input(f"Please select action [{config.get_mail_client_actions_as_string()}]: ")
            wrapper_class_mail_action = config.get_mail_client_action_as_class(action)(logger, config,ip_address,SMTP_port, POP3_port, username, password)
            logger.info(f"succesfully starting {wrapper_class_mail_action} action")
            wrapper_class_mail_action.action()
        except Exception as e:
            print(f"Error: {e}")



if __name__ == "__main__":
    logger = get_logger()
    config = ConfigWrapper(logger,"general_config")
    main(logger,config)
