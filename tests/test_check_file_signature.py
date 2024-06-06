import os
import pytest


@pytest.mark.parametrize("start_server", [{"threads": 10}], indirect=True)
def test_check_file_signature(start_server, start_client):
    project_root = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(os.path.join(project_root, 'files_for_tests/text.txt'))
    # protected_file_path = os.path.join(project_root, 'files_for_tests/protected_file.txt')

    client_params_list = [
        {"command": "CheckLocalFile", "params": {"param1": file_path, "param2": "Hurricane"}},
        {"command": "CheckLocalFile", "params": {"param1": "/nonexistent/file/tmp", "param2": "Hurricane"}},
        # {"command": "CheckLocalFile", "params": {"param1": protected_file_path, "param2": "some"}},
        # For last case, you need to create a file that is only accessible to the root user or any other group
    ]

    massages = [
        "Received: Signature offsets: [11, 224, 1923, 4326]",
        "Received: File not found: /nonexistent/file/tmp",
        # f"Received: Permission denied to {protected_file_path}",
    ]

    for params, massage in zip(client_params_list, massages):
        client_output = start_client(params)
        assert massage in client_output
