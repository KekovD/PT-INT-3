import subprocess
import time
import signal
import pytest


@pytest.mark.parametrize(
    "host, port, threads, expected_stdout, expected_stderr",
    [
        ("localhost", "16000", "2", "Server started at ('localhost', 16000)\nServer stopped\n", ""),
        ("localhost", "16000", "0", "The thread number 0 must be positive and non-null\n", ""),
    ]
)
def test_start_server(server_script, quarantine_dir, host, port, threads, expected_stdout, expected_stderr):
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
