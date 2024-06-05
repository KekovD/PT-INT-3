import json

from src.server.config import logger
from src.server.responsibility_chain.CommandBase import CommandBase


class TCPHandler:
    def __init__(self, request, client_address, server, command_chain: CommandBase):
        self.data = None
        self.request = request
        self.client_address = client_address
        self.server = server
        self.handle()
        self.command_chain = command_chain

    def handle(self) -> None:
        self.data = self.request.recv(1024).strip()
        self.data = json.loads(self.data)
        self.validate_request(self.data)
        self.command_chain.handle(self.request, self.data, self.server)

    def validate_request(self, request: json) -> None:
        if request:
            required_keys = {"command", "params"}
            actual_keys = set(request.keys())
            extra_keys = required_keys.difference(actual_keys)
            missing_keys = required_keys.difference(actual_keys)

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
                return

            logger.info("Request is valid")

        else:
            response = "Request is empty".encode("utf-8")
            self.request.sendall(response)
            logger.warning("Request is empty")
            self.request.close()
