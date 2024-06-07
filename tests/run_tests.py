import os
import subprocess


def main() -> None:
    subprocess.run(['pytest', '--tb=short', os.path.dirname(os.path.abspath(__file__))], text=True)


if __name__ == '__main__':
    main()
