import os
import pytest
import subprocess
import time
import signal


@pytest.fixture(scope='session')
def host():
    return 'localhost'


@pytest.fixture(scope='session')
def port():
    return "2020"


@pytest.fixture(scope='session')
def server_script():
    return "../src/server/server.py"


@pytest.fixture(scope='session')
def quarantine_dir():
    return os.path.join(os.path.dirname(__file__), 'quarantine')


@pytest.fixture(scope='session')
@pytest.mark.usefixtures('host', 'port', 'server_script', 'quarantine_dir')
def start_server(request, host, port, server_script, quarantine_dir):
    threads = request.param['threads']

    args = ["python", server_script, host, port, str(threads), quarantine_dir]

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(3)

    yield process

    process.send_signal(signal.SIGINT)
    process.wait()


@pytest.fixture(scope='session')
@pytest.mark.usefixtures('host', 'port')
def start_client(request, host, port):
    def _start_client(params):
        command = params['command']
        client_params = params['params']

        client_script = "../src/client/client.py"

        params_list = [f"{k}={v}" for k, v in client_params.items()]
        client_args = ["python", client_script, host, port, command] + params_list

        result = subprocess.run(client_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Client script failed with error:\n{result.stderr}")

        return result.stdout.strip()

    return _start_client
