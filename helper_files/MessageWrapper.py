from structlog import BoundLogger

import ConfigWrapper

class MessageWrapper():
    def __init__(self, logger: BoundLogger, config: ConfigWrapper ,message: str) -> str:
        self._message = message
        self._config = config
        self._logger = logger
    
    def __str__(self) -> str:
        return self._message
    
    def __getFromIndex(self) -> int:
        return self._message.find(self.getFrom()) + len(self._config.getFrom())
    
    def __getToIndex(self) -> int:
        return self._message.find(self.getTo()) + len(self._config.getTo())
    
    def __getSubjectIndex(self) -> int:
        return self._message.find(self.getSubject()) + len(self._config.getSubject())
    
    def __getReceivedIndex(self) -> int:
        return self._message.find(self.getReceived()) + len(self._config.getReceived())
      
    def getFrom(self) -> str:
        return self._message[self.__getFromIndex:self.__getToIndex]
    
    def getTo(self) -> str:
        return self._message[self.__getToIndex:self.__getSubjectIndex]
    
    def getSubject(self) -> str:
        return self._message[self.__getSubjectIndex:self._config.getDateLen()]
    
    def getReceived(self) -> str:
        return self._message[self.__getReceivedIndex:]
    
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
        #TODO: verifying format of message, return True when format is correct
        pass