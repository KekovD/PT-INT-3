import os
import subprocess
import time
import signal
import pytest


@pytest.mark.parametrize(
    "host, port, threads, wrong_quarantine_dir, expected_stdout, expected_stderr",
    [
        ("localhost", "16000", "2", None, "Server started at ('localhost', 16000)\nServer stopped\n", ""),
        ("localhost", "16000", "0", None, "The thread number 0 must be positive and non-null\n", ""),
        ("localhost", "16000", "2", "files_for_tests/text.txt", "Error: QUARANTINE_PATH is a file, not a directory.\n", ""),
    ]
)
def test_start_server(
        server_script,
        quarantine_dir,
        host,
        port,
        threads,
        expected_stdout,
        expected_stderr,
        wrong_quarantine_dir
):
    if wrong_quarantine_dir:
        quarantine_dir = os.path.join(os.path.dirname(__file__), wrong_quarantine_dir)

    args = ["python", server_script, host, port, threads, quarantine_dir]

    first_case = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(5)

    first_case.send_signal(signal.SIGINT)

    try:
        stdout, stderr = first_case.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        first_case.kill()
        stdout, stderr = first_case.communicate()

    stdout_decoded = stdout.decode('utf-8')
    stderr_decoded = stderr.decode('utf-8')

    assert stdout_decoded == expected_stdout
    assert stderr_decoded == expected_stderr
