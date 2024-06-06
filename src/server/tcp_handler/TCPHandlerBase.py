import socket

from abc import ABC
from src.server.responsibility_chain import CommandBase
from src.server.threaded_tcp_server import ThreadedTCPServer


class TCPHandlerBase(ABC):
    def __init__(
            self,
            request: socket.socket,
            client_address: tuple[str, int],
            server: ThreadedTCPServer,
            command_chain: CommandBase
    ):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.command_chain = command_chain
        self.data = None

    def handle(self) -> None:
        pass
