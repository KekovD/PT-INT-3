import json
import os
import shutil

from src.server.config import logger
from src.server.responsibility_chain.CommandBase import CommandBase


class QuarantineLocalFileCommand(CommandBase):
    def handle(self, request, data: json, server):
        if data.get("command") == 'QuarantineLocalFile':
            required_params = {"param1"}
            provided_params = set(data["params"].keys())

            if not self._verify_params(required_params, provided_params, request):
                return

            local_file_path = data.get("params", {}).get("param1")

            if local_file_path is None:
                response = f"Invalid query format. Local file path missing in param1.".encode("utf-8")
                request.sendall(response)
                logger.info("Invalid query format. Local file path missing in param1")
                request.close()
                return

            if not os.path.exists(server.quarantine_path):
                os.makedirs(server.quarantine_path)

            try:
                shutil.move(local_file_path, server.quarantine_path)
                response = f"File moved from {local_file_path} to quarantine {server.quarantine_path}".encode("utf-8")
                request.sendall(response)
                logger.info(f"File moved from {local_file_path} to quarantine {server.quarantine_path}")
                request.close()

            except FileNotFoundError:
                response = f"File not found: {local_file_path}".encode("utf-8")
                request.sendall(response)
                logger.info(f"File not found: {local_file_path}")
                request.close()

            except PermissionError:
                response = f"Permission denied to {local_file_path}".encode("utf-8")
                request.sendall(response)
                logger.warning(f"Permission denied to {local_file_path}")
                request.close()

            except Exception as e:
                response = "Error moving a file to quarantine".encode("utf-8")
                request.sendall(response)
                logger.error(f"Error in TCPHandler.quarantine_local_file(): {e}")
                request.close()

        elif self.next is not None:
            self.next.handle(request, data, server)

        else:
            response = f"Unknown command '{data}.".encode("utf-8")
            request.sendall(response)
            logger.warning(f"Unknown command '{data}.'")
            request.close()
