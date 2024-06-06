import os
import socket
import pytest


def send_and_receive(host: str, port: str, data: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, int(port)))
        sock.sendall(data.encode('utf-8'))
        received = sock.recv(1024).decode('utf-8')
    return received


@pytest.mark.parametrize("start_server", [{"threads": 10}], indirect=True)
def test_invalid_command_and_params_sent(start_server, start_client, host, port):
    large_signature = ""
    while len(large_signature) < 1100:
        large_signature += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    project_root = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(os.path.join(project_root, 'files_for_tests/text.txt'))
    large_request = ""

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            large_request = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

    client_params_list = [
        {"command": "example_command", "params": {"param1": "value1"}},
        {"command": "QuarantineLocalFile", "params": {"param": "value"}},
        {"command": "QuarantineLocalFile", "params": {"param1": ""}},
        {"command": "CheckLocalFile", "params": {"param1": "value", "param2": ""}},
        {"command": "CheckLocalFile", "params": {"param1": "", "param2": ""}},
        {"command": "CheckLocalFile", "params": {"param1": "value", "param2": large_signature}},
        {"command": "CheckLocalFile", "params": {"param1": "value", "param2": large_request}},
    ]

    error_msgs = [
        "Received: Unknown command",
        "Received: Invalid query format. Parameters missing: param1, Extra parameters provided: param",
        "Received: Invalid query format. Local file path cannot be empty in param1",
        "Received: Invalid query format. Parameters cannot be empty: signature - param2",
        "Received: Invalid query format. Parameters cannot be empty: local file path - param1, signature - param2",
        "Received: Invalid query format. Signature is too large",
        "Received: Message exceeds 2048 bytes. Request too large",
    ]

    for params, error_msg in zip(client_params_list, error_msgs):
        client_output = start_client(params)
        assert error_msg in client_output

    test_cases = [
        (
            '''{"command": "CheckLocalFile", "temp": {"param1": "Path"}}''',
            "Invalid query format. Missing keys: params. Invalid keys: temp"
        ),
        (
            "temp",
            "Invalid JSON format. Request must be in JSON format."
        ),
        (
            "{ }",
            "Request is empty"
        )
    ]

    for data, expected_result in test_cases:
        received = send_and_receive(host, port, data)
        assert received == expected_result
