from structlog import BoundLogger


import regex

from helper_files.ConfigWrapper import ConfigWrapper


class MessageWrapper():
    def __init__(self, logger: BoundLogger, config: ConfigWrapper ,message: str) -> None:
        self._message = message
        self._config = config
        self._logger = logger
    
    def __str__(self) -> str:
        return self._message
    
    def __getFromIndex(self) -> int:
        to_str = self.getTo()
        return self._message.find(to_str) + len(to_str)
    
    def __getToIndex(self) -> int:
        from_str = self.getFrom()
        return self._message.find(from_str, self.__getFromIndex()) + len(from_str)

    def __getSubjectIndex(self) -> int:
        return self._message.find(self.getSubject()) + len(self._config.getSubjectConfig())
    
    def __getReceivedIndex(self) -> int:
        return self._message.find(self.getReceived()) + len(self._config.getRecievedConfig())
      
    def getFrom(self) -> str:
        return self._message[self.__getFromIndex():self.__getToIndex()]
    
    def getTo(self) -> str:
        from_str = self.getFrom()
        return self._message[self._message.find(from_str) + len(from_str):self.__getSubjectIndex()]
    """
    def getTo(self) -> str:
        return self._message[self.__getToIndex():self.__getSubjectIndex()]
    """
    
    def getSubject(self) -> str:
        return self._message[self.__getSubjectIndex:self._config.getDateLen()]
    
    def getReceived(self) -> str:
        return self._message[self.__getReceivedIndex():]
    
    def getFromUsername(self) -> str:
        return self.getFrom().split("@")[0]
    
    def getFromDomain_name(self) -> str:
        return self.getFrom().split("@")[1]
    
    def getToUsername(self) -> str:
        return self.getTo().split("@")[0]
    
    def getToDomain_name(self) -> str:
        return self.getTo().split("@")[1]
    
    def getMessageBody(self) -> str:
        return self._message
    
    def verify_format(self) -> bool:
        pattern = r'^From: \S+@\S+\nTo: \S+@\S+\nSubject: .{1,150}\n(.+\n)*\.$'
        return bool(regex.match(pattern, self._message))

 