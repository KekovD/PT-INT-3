import json
import socket

from abc import ABC, abstractmethod
from src.server.config import logger
from src.server.threaded_tcp_server import ThreadedTCPServer


class CommandBase(ABC):
    def __init__(self):
        self.next = None

    def add_next(self, next_command: 'CommandBase') -> None:
        if self.next:
            self.next.add_next(next_command)
        else:
            self.next = next_command

    @staticmethod
    def _verify_params(required_params: set[str], provided_params: set[str], request) -> bool:
        missing_params = required_params - provided_params
        extra_params = provided_params - required_params

        error_messages = []
        if missing_params:
            error_messages.append(f"Parameters missing: {', '.join(missing_params)}")
        if extra_params:
            error_messages.append(f"Extra parameters provided: {', '.join(extra_params)}")

        if error_messages:
            response = ("Invalid query format. " + ", ".join(error_messages)).encode("utf-8")
            request.sendall(response)
            logger.info("Invalid query format. " + ", ".join(error_messages))
            request.close()
            return False
        
        return True

    @staticmethod
    def _send_response(request: socket.socket, message: str, log_func: logger) -> None:
        response = message.encode("utf-8")
        request.sendall(response)
        log_func(message)
        request.close()

    @abstractmethod
    def handle(self, request: socket.socket, data: json, server: ThreadedTCPServer) -> None:
        pass
