import os
import shutil
import pytest


@pytest.mark.parametrize("start_server", [{"threads": 10}], indirect=True)
def test_move_file_to_quarantine(start_server, start_client):
    project_root = os.path.dirname(os.path.abspath(__file__))
    file_directory = os.path.join(project_root, 'files_for_tests')
    second_file_directory = os.path.join(file_directory, 'second_file')

    if not os.path.exists(file_directory):
        os.makedirs(file_directory)

    if not os.path.exists(second_file_directory):
        os.makedirs(second_file_directory)

    quarantine_directory = os.path.join(project_root, 'quarantine')

    quarantine_file = 'quarantine_file.txt'
    second_quarantine_file = 'quarantine_file(1).txt'

    file_path = os.path.join(file_directory, quarantine_file)
    with open(file_path, 'w') as file:
        file.write("This is a quarantine file.")

    second_file_path = os.path.join(second_file_directory, quarantine_file)
    with open(second_file_path, 'w') as file:
        file.write("This is a second quarantine file.")

    # protected_file_path = os.path.join(project_root, 'files_for_tests/protected_file.txt')

    client_params_list = [
        {"command": "QuarantineLocalFile", "params": {"param1": "/nonexistent/file/tmp"}},
        {"command": "QuarantineLocalFile", "params": {"param1": file_path}},
        {"command": "QuarantineLocalFile", "params": {"param1": second_file_path}},
        {"command": "QuarantineLocalFile", "params": {"param1": file_path}},
        {"command": "QuarantineLocalFile", "params": {"param1": file_directory}},
        # {"command": "QuarantineLocalFile", "params": {"param1": protected_file_path}},
        # For last case, you need to create a file that is only accessible to the root user or any other group
    ]

    massages = [
        "Received: File not found: /nonexistent/file/tmp",
        f"Received: File moved from {file_path} to quarantine",
        f"Received: File moved from {second_file_path} to quarantine",
        f"Received: File not found:",
        f"Received: {file_directory} is a directory, not a file",
        # f"Received: Permission denied to {protected_file_path}",
    ]

    quarantine_file_path = os.path.join(quarantine_directory, quarantine_file)
    second_quarantine_file_path = os.path.join(quarantine_directory, second_quarantine_file)

    for case, (params, massage) in enumerate(zip(client_params_list, massages)):
        client_output = start_client(params)
        assert massage in client_output

        if case == 0:
            assert os.path.exists(quarantine_directory) is True
        if case == 1:
            assert os.path.exists(quarantine_file_path) is True
        if case == 2:
            assert os.path.exists(second_quarantine_file_path) is True

    for path in [quarantine_file_path, second_quarantine_file_path]:
        if os.path.exists(path):
            os.remove(path)

    if os.path.exists(second_file_directory):
        shutil.rmtree(second_file_directory)
