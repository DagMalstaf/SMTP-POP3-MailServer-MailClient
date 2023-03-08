from typing import List, Dict
from structlog import BoundLogger
import yaml
from yaml.loader import SafeLoader

from custom_exceptions.ConfigReadError import ConfigReadError
from helper_files import Action

CLIENT_ACTIONS: Dict[str,Action] ={
    "Mail Sending": Action ,
    "Mail Management": Action,
    "Exit":Action
}
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

    def get_mail_client_actions_as_list_of_strings(self) -> List[str]:
        return self._loaded_config_dictionary["actions_for_mail_cient"]

    @staticmethod
    def get_mail_client_actions_as_list_of_classes() -> List[Action]:
        return list(CLIENT_ACTIONS.values())

    def get_mail_client_actions_as_string(self) -> str:
        return ', '.join(self.get_mail_client_actions_as_list_of_strings())

    def get_mail_client_action_as_class(self, action: str) -> Action:
        try:
            return CLIENT_ACTIONS.get(action)
        except KeyError as e:
            self._logger.info(f"Invalid action given for mail client: {action}\n"
                              f"Possible actions are: [{self.get_mail_client_actions_as_string()}]")
            raise e

    def get_message_format(self) -> str:
        return self._loaded_config_dictionary["message_format"]