import socket
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="TCP client script")
    parser.add_argument("host", type=str, help="Host to connect to")
    parser.add_argument("port", type=int, help="Port to connect to")
    parser.add_argument("command", type=str, help="Command to send")
    parser.add_argument("params", nargs='+', help="List of parameters in the form 'param_name=param_value'")

    args = parser.parse_args()

    host, port = args.host, args.port
    command = args.command
    params = {}

    for param in args.params:
        name, value = param.split('=', 1)
        params[name] = value

    data = json.dumps({
        "command": command,
        "params": params
    })

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.sendall(data.encode('utf-8'))
            received = sock.recv(1024)
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"Sent: {data}")
    print(f"Received: {received.decode('utf-8')}")


if __name__ == "__main__":
    main()
