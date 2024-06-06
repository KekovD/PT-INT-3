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
    server_process = start_server
    assert server_process is not None

    long_signature = ""

    while len(long_signature) < 1100:
        long_signature += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    client_params_list = [
        {"command": "example_command", "params": {"param1": "value1"}},
        {"command": "QuarantineLocalFile", "params": {"param": "value"}},
        {"command": "QuarantineLocalFile", "params": {"param1": ""}},
        {"command": "CheckLocalFile", "params": {"param1": "value", "param2": ""}},
        {"command": "CheckLocalFile", "params": {"param1": "", "param2": ""}},
        {"command": "CheckLocalFile", "params": {"param1": "value", "param2": long_signature}},
    ]

    error_msgs = [
        "Received: Unknown command",
        "Received: Invalid query format. Parameters missing: param1, Extra parameters provided: param",
        "Received: Invalid query format. Local file path cannot be empty in param1",
        "Received: Invalid query format. Parameters cannot be empty: signature - param2",
        "Received: Invalid query format. Parameters cannot be empty: local file path - param1, signature - param2",
        "Received: Invalid query format. Signature is too long",
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
