import socket
from concurrent.futures import ThreadPoolExecutor


class ThreadedTCPServer:
    def __init__(self, server_address, handler_class, max_threads, quarantine_path, command_chain):
        self.server_address = server_address
        self.handler_class = handler_class
        self.max_threads = max_threads
        self.quarantine_path = quarantine_path
        self.is_running = False
        self.command_chain = command_chain

    def start(self):
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
                        request, client_address,
                        self,
                        self.command_chain
                    )

    def stop(self):
        self.is_running = False
