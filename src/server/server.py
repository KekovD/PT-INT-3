import argparse

from tcp_handler.TCPHandler import TCPHandler
from threaded_tcp_server.ThreadedTCPServer import ThreadedTCPServer
from responsibility_chain.CheckLocalFileCommand import CheckLocalFileCommand
from responsibility_chain.QuarantineLocalFileCommand import QuarantineLocalFileCommand


def parse_arguments():
    parser = argparse.ArgumentParser(description="Start the TCP Server with specified parameters.")
    parser.add_argument('HOST', type=str, help='Hostname or IP address to bind the server to.')
    parser.add_argument('PORT', type=int, help='Port number to bind the server to.')
    parser.add_argument('MAX_THREADS', type=int, help='Maximum number of threads for the server.')
    parser.add_argument('QUARANTINE_PATH', type=str, help='Path to the quarantine directory.')

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    server_address = (args.HOST, args.PORT)
    quarantine_path = args.QUARANTINE_PATH

    command_chain = CheckLocalFileCommand()
    quarantine_command = QuarantineLocalFileCommand()
    command_chain.add_next(quarantine_command)

    server = ThreadedTCPServer(
        server_address,
        TCPHandler,
        args.MAX_THREADS,
        quarantine_path,
        command_chain)

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("Server stopped")


if __name__ == "__main__":
    main()
