from typing import Callable

from structlog import BoundLogger


import regex

from helper_files.ConfigWrapper import ConfigWrapper


class MessageWrapper():

    def __init__(self, logger: BoundLogger, config: ConfigWrapper, message: str) -> None:
        self._message = message
        self._config = config
        self._logger = logger
    
    def __str__(self) -> str:
        return self._message
    
    def __get_from_index(self) -> int:
        return self._message.find(self._config.get_from_config()) + len(self._config.get_from_config())
    
    def __get_to_index(self) -> int:
        return self._message.find(self._config.get_to_config()) + len(self._config.get_to_config())

    def __get_subject_index(self) -> int:
        return self._message.find(self._config.get_subject_config()) + len(self._config.get_subject_config())
    
    def __get_received_index(self) -> int:
        return self._message.find(self._config.get_received_config()) + len(self._config.get_received_config())
    
    def __get_end_line_index_from(self, index: int):
        return self._message.find(self._config.get_end_line_character(), index)
    
    def __get_sub_message(self, index: int):
        return self._message[index:self.__get_end_line_index_from(index)]
        return self._message[self._message.find(from_str) + len(from_str):self.__getSubjectIndex()]
    """
    def getTo(self) -> str:
        return self._message[self.__getToIndex():self.__getSubjectIndex()]
    """
      
    def get_from(self) -> str:
        return self.__get_sub_message(self.__get_from_index())
    
    def get_to(self) -> str:
        return self.__get_sub_message(self.__get_to_index())
    
    def get_subject(self) -> str:
        return self.__get_sub_message(self.__get_subject_index())
    
    def get_received(self) -> str:
        return self.__get_sub_message(self.__get_received_index())

    def __get_username(self, slice_function) -> str:
        return slice_function().split(self._config.get_mail_separator())[0]

    def __get_domain(self, slice_function: Callable[..., str]):
        return (domain := slice_function().split(self._config.get_mail_separator())[1])\
            [:domain.rfind(self._config.get_domain_mail_separator())]

    def get_from_username(self) -> str:
        return self.__get_username(self.get_from)

    def get_from_domain_name(self) -> str:
        return self.__get_domain(self.get_from)
    
    def get_to_username(self) -> str:
        return self.__get_username(self.get_to)
    
    def get_to_domain_name(self) -> str:
        return self.__get_domain(self.get_to)
    
    def get_message_body(self) -> str:
        return (message_body := self._message[self.__get_end_line_index_from(self.__get_subject_index())+1:])\
                    [:message_body.rfind(self._config.get_end_line_character())]
    
    def verify_format(self) -> bool:
        pattern = r'^From: \S+@\S+\nTo: \S+@\S+\nSubject: .{1,150}\n(.+\n)*\.$'
        return bool(regex.match(pattern, self._message))

 