from abc import ABC, abstractmethod

class AbstractChatCommands(ABC):
    @abstractmethod
    def processUserCommands(self, message, username, ci): pass

    @abstractmethod
    def processBroadcasterCommands(self, message, ci): pass
