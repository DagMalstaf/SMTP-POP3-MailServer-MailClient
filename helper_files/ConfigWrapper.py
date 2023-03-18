
from typing import List, Dict, Callable
from structlog import BoundLogger
import yaml
from yaml.loader import SafeLoader

from custom_exceptions.ConfigReadError import ConfigReadError


class ConfigWrapper:
    def __init__(self,logger: BoundLogger , file_name: str):
        with open(f"config_files/{file_name}.yaml", "r") as config:
            try:
                # Converts yaml document to python object
                self._loaded_config_dictionary = yaml.load(config, Loader=SafeLoader)
                self._logger = logger

            except yaml.YAMLError as e:
                raise ConfigReadError(f"Unable to load config file, error:\n"
                                      f"{e}")
    

    def get_from_config(self) -> str:
        return self._loaded_config_dictionary.get("from")
    
    def get_to_config(self) -> str:
        return self._loaded_config_dictionary.get("to")
    
    def get_subject_config(self) -> str:
        return self._loaded_config_dictionary.get("subject")
    
    def get_received_config(self) -> str:
        return self._loaded_config_dictionary.get("received")
    
    def get_date_length(self) -> int:
        return len(self._loaded_config_dictionary.get("date_length"))

    def get_mail_client_actions_as_list_of_strings(self) -> List[str]:
        return self._loaded_config_dictionary["actions_for_mail_cient"]

    def get_mail_management_actions_as_list_of_strings(self) -> List[str]:
        return self._loaded_config_dictionary["actions_for_mail_management"]

    @staticmethod
    def get_mail_management_actions_as_list_of_functions() -> List[Callable[...,None]]:
        # Calllable[argument types, return type] ... means any type is good (doesn't really matter to define here)
        return list(MAIL_MANAGEMENT_ACTIONS.values())

    def get_mail_client_actions_as_string(self) -> str:
        return ', '.join(self.get_mail_client_actions_as_list_of_strings())

    def get_mail_management_actions_as_string(self) -> str:
        return ', '.join(self.get_mail_management_actions_as_list_of_strings())

    def get_mail_management_action_as_fuction(self, action: str) -> (...):
        try:
            return MAIL_MANAGEMENT_ACTIONS.get(action)
        except KeyError as e:
            self._logger.info(f"Invalid action given for mail client: {action}\n"
                              f"Possible actions are: [{self.get_mail_management_actions_as_string()}]")
            raise e

    def get_message_format(self) -> str:
        return self._loaded_config_dictionary["message_format"]

    def get_stopping_character(self) -> str:
        return self._loaded_config_dictionary["stopping_character"]

    def get_host(self) -> str:
        return self._loaded_config_dictionary["host"]

    def get_max_size_package_tcp(self) -> int:
        return self._loaded_config_dictionary["max_size_package_tcp"]
    
    def get_max_thread_load(self) -> int:
        return self._loaded_config_dictionary["max_thread_load"]

    def get_end_line_character(self) -> str:
        return self._loaded_config_dictionary["end_line_character"]

    def get_mail_separator(self) -> str:
        return self._loaded_config_dictionary["mail_separator_sign"]

    def get_domain_mail_separator(self) -> str:
        return self._loaded_config_dictionary["mail_domain_separator"]
