import socket
import pytest


def send_and_receive(host: str, port: str, data: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, int(port)))
        sock.sendall(data.encode('utf-8'))
        received = sock.recv(1024).decode('utf-8')
    return received


@pytest.mark.parametrize("start_server", [{"threads": 10}], indirect=True)
@pytest.mark.parametrize(
    "client_params, expected_error_msg, data, expected_result",
    [
        (
            {"command": "example_command", "params": {"param1": "value1"}},
            "Received: Unknown command",
            None,
            None
        ),
        (
            {"command": "QuarantineLocalFile", "params": {"param": "value"}},
            "Received: Invalid query format. Parameters missing: param1, Extra parameters provided: param",
            None,
            None
        ),
        (
            {"command": "QuarantineLocalFile", "params": {"param1": ""}},
            "Received: Invalid query format. Local file path cannot be empty in param1",
            None,
            None
        ),
        (
            {"command": "CheckLocalFile", "params": {"param1": "value", "param2": ""}},
            "Received: Invalid query format. Parameters cannot be empty: signature - param2",
            None,
            None
        ),
        (
            {"command": "CheckLocalFile", "params": {"param1": "", "param2": ""}},
            "Received: Invalid query format. Parameters cannot be empty: local file path - param1, signature - param2",
            None,
            None
        ),
        (
            {"command": "CheckLocalFile", "params": {"param1": "value", "param2": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" * 22}},
            "Received: Invalid query format. Signature is too large",
            None,
            None
        ),
        (
            {"command": "CheckLocalFile", "params": {"param1": "value", "param2": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" * 44}},
            "Received: Message exceeds 2048 bytes. Request too large",
            None,
            None
        ),
        (
            None,
            None,
            '{"command": "CheckLocalFile", "temp": {"param1": "Path"}}',
            "Invalid query format. Missing keys: params. Invalid keys: temp"
        ),
        (
            None,
            None,
            "temp",
            "Invalid JSON format. Request must be in JSON format."
        ),
        (
            None,
            None,
            "{ }",
            "Request is empty"
        ),
    ]
)
def test_invalid_command_and_params_sent(
        start_server,
        start_client,
        host,
        port,
        client_params,
        expected_error_msg,
        data,
        expected_result
):
    if client_params:
        client_output = start_client(client_params)
        assert expected_error_msg in client_output

    if data:
        received = send_and_receive(host, port, data)
        assert received == expected_result
