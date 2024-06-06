import socket
from concurrent.futures import ThreadPoolExecutor
from src.server.responsibility_chain import CommandBase
from src.server.tcp_handler import TCPHandlerBase


class ThreadedTCPServer:
    def __init__(
            self,
            server_address: tuple[str, int],
            handler_class: TCPHandlerBase,
            max_threads: int,
            quarantine_path: str,
            command_chain: CommandBase
    ):
        self.server_address = server_address
        self.handler_class = handler_class
        self.max_threads = max_threads
        self.quarantine_path = quarantine_path
        self.is_running = False
        self.command_chain = command_chain

    def start(self) -> None:
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            self.is_running = True
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(self.server_address)
                sock.listen()
                print(f"Server started at {self.server_address}")

                while self.is_running:
                    request, client_address = sock.accept()
                    executor.submit(
                        self.handler_class,
                        request,
                        client_address,
                        self,
                        self.command_chain
                    )

    def stop(self) -> None:
        self.is_running = False
