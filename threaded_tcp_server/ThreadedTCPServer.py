import os
import socket

from concurrent.futures import ThreadPoolExecutor
from responsibility_chain import CommandBase
from server_config import logger
from tcp_handler import TCPHandlerBase


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
        if self.max_threads <= 0:
            print(f"The thread number {self.max_threads} must be positive and non-null")
            return

        if not self.__ensure_directory_exists(self.quarantine_path):
            return

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

    @staticmethod
    def __ensure_directory_exists(path: str) -> bool:
        try:
            if os.path.isfile(path):
                print(f"Error: QUARANTINE_PATH is a file, not a directory.")
                return False

            if not os.path.exists(path):
                os.makedirs(path)

            return True

        except PermissionError:
            print(f"Permission denied to create directory {path}")
            return False

        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
