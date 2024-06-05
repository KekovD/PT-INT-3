import json
from abc import ABC, abstractmethod


class CommandBase(ABC):
    def __init__(self):
        self.next = None

    def add_next(self, next_command: 'CommandBase') -> None:
        if self.next:
            self.next.add_next(next_command)
        else:
            self.next = next_command

    @abstractmethod
    def handle(self, request, data: json, server):
        pass
