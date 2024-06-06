import json
import os
import shutil
import socket

from src.server.config import logger
from src.server.responsibility_chain.CommandBase import CommandBase
from src.server.threaded_tcp_server import ThreadedTCPServer


class QuarantineLocalFileCommand(CommandBase):

    def handle(self, request: socket.socket, data: json, server: ThreadedTCPServer) -> None:
        if data.get("command") == 'QuarantineLocalFile':
            required_params = {"param1"}
            provided_params = set(data["params"].keys())

            if not self._verify_params(required_params, provided_params, request):
                return

            local_file_path = data.get("params", {}).get("param1")

            if local_file_path is None:
                self._send_response(request, "Invalid query format. Local file path missing in param1.", logger.info)
                return

            self.__ensure_directory_exists(server.quarantine_path, request)

            self.__move_file_to_quarantine(local_file_path, server.quarantine_path, request)

        elif self.next is not None:
            self.next.handle(request, data, server)
        else:
            self._send_response(request, f"Unknown command '{data}'.", logger.warning)

    def __ensure_directory_exists(self, path: str, request: socket.socket) -> None:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except PermissionError:
            self._send_response(request, f"Permission denied to create directory {path}", logger.warning)
        except Exception as e:
            self._send_response(request, f"Error creating directory {path}: {e}", logger.error)

    def __move_file_to_quarantine(self, src_path: str, dest_path: str, request: socket.socket) -> None:
        try:
            shutil.move(src_path, dest_path)
            message = f"File moved from {src_path} to quarantine {dest_path}"
            self._send_response(request, message, logger.info)
        except FileNotFoundError:
            self._send_response(request, f"File not found: {src_path}", logger.info)
        except PermissionError:
            self._send_response(request, f"Permission denied to {src_path}", logger.warning)
        except Exception as e:
            self._send_response(request, f"Error moving a file to quarantine: {e}", logger.error)
