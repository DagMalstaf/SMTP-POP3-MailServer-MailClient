import yaml
from yaml.loader import SafeLoader

from custom_exceptions.ConfigReadError import ConfigReadError


class WrapperConfig:
    def __init__(self,file_name: str):
        with open(f"config_files/{file_name}.yaml", "r") as config:
            try:
                # Converts yaml document to python object
                self._loaded_config_dictionary = yaml.load(config, Loader=SafeLoader)

            except yaml.YAMLError as e:
                raise ConfigReadError(f"Unable to load config file, error:\n"
                                      f"{e}")
    

    def getFromConfig(self) -> str:
        return self._loaded_config_dictionary.get("FROM")
    
    def getToConfig(self) -> str:
        return self._loaded_config_dictionary.get("TO")
    
    def getSubjectConfig(self) -> str:
        return self._loaded_config_dictionary.get("SUBJECT")
    
    def getRecievedConfig(self) -> str:
        return self._loaded_config_dictionary.get("RECIEVED")
    
    def getDateLen(self) -> int:
        return len(self._loaded_config_dictionary.get("DATE"))

