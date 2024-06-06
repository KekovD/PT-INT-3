import json
import socket

from src.server.config import logger
from src.server.responsibility_chain import CommandBase
from src.server.tcp_handler.TCPHandlerBase import TCPHandlerBase
from src.server.threaded_tcp_server import ThreadedTCPServer


class TCPHandler(TCPHandlerBase):
    def __init__(
            self,
            request: socket.socket,
            client_address: tuple[str, int],
            server: ThreadedTCPServer,
            command_chain: CommandBase
    ):
        super().__init__(request, client_address, server, command_chain)
        self.handle()

    def handle(self) -> None:
        try:
            self.data = self.request.recv(2048).strip()
            self.data = json.loads(self.data)

        except json.JSONDecodeError:
            response = "Invalid JSON format. Request must be in JSON format.".encode("utf-8")
            self.request.sendall(response)
            logger.warning("Invalid JSON format. Request must be in JSON format.")
            self.request.close()
            return

        if not self.validate_request(self.data):
            return

        self.command_chain.handle(self.request, self.data, self.server)

    def validate_request(self, request: json) -> bool:
        if request:
            required_keys = {"command", "params"}
            actual_keys = set(request.keys())

            missing_keys = required_keys.difference(actual_keys)
            extra_keys = actual_keys.difference(required_keys)

            error_messages = []

            if missing_keys:
                missing_keys_str = ', '.join(missing_keys)
                error_messages.append(f"Missing keys: {missing_keys_str}")

            if extra_keys:
                extra_keys_str = ', '.join(extra_keys)
                error_messages.append(f"Invalid keys: {extra_keys_str}")

            if error_messages:
                combined_error_message = '. '.join(error_messages)
                response = f"Invalid query format. {combined_error_message}".encode("utf-8")
                self.request.sendall(response)
                logger.warning(f"Invalid query format. {combined_error_message}")
                self.request.close()
                return False

            return True

        else:
            response = "Request is empty".encode("utf-8")
            self.request.sendall(response)
            logger.warning("Request is empty")
            self.request.close()
            return False
