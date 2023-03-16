from structlog import BoundLogger
from multiprocessing import get_logger

from custom_exceptions.RestartMailServerError import RestartMailServerError
from helper_files.ConfigWrapper import ConfigWrapper
from helper_files.functions.general_helper_functions import get_parameters_mail_client, retrieve_command_promt_input
from helper_files.functions.mail_functions import get_action

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
    ip_address, SMTP_port, POP3_port, username, password = get_parameters_mail_client()
    while True:
        try:
            action = retrieve_command_promt_input(f"Please select action [{config.get_mail_client_actions_as_string()}]: ")
            wrapper_class_mail_action = get_action(logger,action)(logger, config,ip_address,SMTP_port, POP3_port, username, password)
            logger.info(f"succesfully starting {wrapper_class_mail_action} action")
            wrapper_class_mail_action.action()
        except Exception as e:
            print(f"Error: {e}")



if __name__ == "__main__":
    logger = get_logger()
    config = ConfigWrapper(logger,"general_config")
    try:
        main(logger,config)
    except RestartMailServerError as e:
        main(logger, config)