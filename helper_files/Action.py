from abc import ABC, abstractmethod


class Action(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def action(self):
        pass
