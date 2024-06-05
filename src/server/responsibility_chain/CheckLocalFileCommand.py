import base64
import json

from src.server.config import logger
from src.server.responsibility_chain.CommandBase import CommandBase


class CheckLocalFileCommand(CommandBase):
    def handle(self, request, data: json, server):
        if data.get("command") == 'CheckLocalFile':

            missing_params = {"param1", "param2"} - set(data["params"].keys())
            if missing_params:
                response = f"Invalid query format. Parameters missing: {', '.join(missing_params)}.".encode("utf-8")
                request.sendall(response)
                logger.info(f"Invalid query format. Parameters missing: {', '.join(missing_params)}.")
                request.close()
                return

            local_file_path = data.get("params", {}).get("param1")
            signature = data.get("params", {}).get("param2")

            if local_file_path is None or signature is None:
                missing_params = []
                if local_file_path is None:
                    missing_params.append("param1")
                if signature is None:
                    missing_params.append("param2")

                response = f"Invalid query format. Parameters missing: {', '.join(missing_params)}.".encode("utf-8")
                request.sendall(response)
                logger.info(f"Invalid query format. Parameters missing: {', '.join(missing_params)}.")
                request.close()
                return

            signature = signature.encode("utf-8")

            if len(signature) > 1024:
                response = "Invalid query format. Signature is too long.".encode("utf-8")
                request.sendall(response)
                logger.info(f"Invalid query format. Signature is too long.")
                request.close()
                return

            try:
                with open(local_file_path, 'rb') as file:
                    file_content = file.read()
                    signature_offsets = []
                    offset = file_content.find(signature)
                    while offset != -1:
                        signature_offsets.append(offset)
                        offset = file_content.find(signature, offset + 1)

                response = f"Signature offsets: {signature_offsets}".encode("utf-8")
                request.sendall(response)
                logger.info(f"Signature offsets: {signature_offsets}, file: {local_file_path}, signature: {signature}")
                request.close()

            except FileNotFoundError:
                response = f"File not found: {local_file_path}".encode("utf-8")
                request.sendall(response)
                logger.warning(f"File not found: {local_file_path}")
                request.close()

            except Exception as e:
                response = "Error processing file".encode("utf-8")
                request.sendall(response)
                logger.error(f"Error processing file: {str(e)}")
                request.close()

        elif self.next is not None:
            self.next.handle(request, data)

        else:
            response = f"Unknown command '{data}.".encode("utf-8")
            request.sendall(response)
            logger.warning(f"Unknown command '{data}.'")
            request.close()
