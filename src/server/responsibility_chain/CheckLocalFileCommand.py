import json
import socket
from typing import List, Callable

from src.server.config import logger
from src.server.responsibility_chain.CommandBase import CommandBase
from src.server.threaded_tcp_server import ThreadedTCPServer


class CheckLocalFileCommand(CommandBase):
    def handle(self, request: socket.socket, data: json, server: ThreadedTCPServer) -> None:
        if data.get("command") == 'CheckLocalFile':
            required_params = {"param1", "param2"}
            provided_params = set(data["params"].keys())

            if not self._verify_params(required_params, provided_params, request):
                return

            local_file_path = data.get("params", {}).get("param1")
            signature = data.get("params", {}).get("param2")

            if local_file_path == "" or signature == "":
                missing_params = []
                if local_file_path == "":
                    missing_params.append("local file path - param1")
                if signature == "":
                    missing_params.append("signature - param2")

                self._send_response(
                    request,
                    f"Invalid query format. Parameters cannot be empty: {', '.join(missing_params)}.",
                    logger.info
                )
                return

            signature = signature.encode("utf-8")

            if len(signature) > 1024:
                self._send_response(
                    request,
                    "Invalid query format. Signature is too long.",
                    logger.info
                )
                return

            self.check_file_signature(local_file_path, signature, request)

        elif self.next is not None:
            self.next.handle(request, data, server)
        else:
            self._send_response(request, f"Unknown command '{data}'.", logger.warning)

    def check_file_signature(self, file_path: str, signature: bytes, request: socket.socket) -> None:
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
                signature_offsets = self.__find_signature_offsets(file_content, signature)

            self._send_response(
                request,
                f"Signature offsets: {signature_offsets}",
                lambda msg: logger.info(f"{msg}, file: {file_path}, signature: {signature}")
            )
        except FileNotFoundError:
            self._send_response(request, f"File not found: {file_path}", logger.warning)
        except Exception as e:
            self._send_response(request, "Error processing file", lambda msg: logger.error(f"{msg}: {str(e)}"))

    @staticmethod
    def __find_signature_offsets(content: bytes, signature: bytes) -> List[int]:
        offsets = []
        offset = content.find(signature)
        while offset != -1:
            offsets.append(offset)
            offset = content.find(signature, offset + 1)
        return offsets
