from src.server.TCPHandler import TCPHandler
from src.server.ThreadedTCPServer import ThreadedTCPServer
from src.server.responsibility_chain.CheckLocalFileCommand import CheckLocalFileCommand
from src.server.responsibility_chain.QuarantineLocalFileCommand import QuarantineLocalFileCommand

if __name__ == "__main__":
    HOST, PORT = "localhost", 1414
    MAX_THREADS = 10

    server_address = (HOST, PORT)

    command_chain = CheckLocalFileCommand()
    quarantine_command = QuarantineLocalFileCommand()
    command_chain.add_next(quarantine_command)

    quarantine_path = '/home/kekov/Downloads/quarantine'

    server = ThreadedTCPServer(
        server_address,
        TCPHandler,
        MAX_THREADS,
        quarantine_path,
        command_chain)

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("Server stopped")
