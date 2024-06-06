from abc import ABC


class TCPHandlerBase(ABC):
    def __init__(self, request, client_address, server, command_chain):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.command_chain = command_chain
        self.data = None

    def handle(self) -> None:
        pass
