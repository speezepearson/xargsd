import argparse
import socket
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socket-file', type=Path, required=True)
parser.add_argument('targets', nargs='*')
args = parser.parse_args()

conn = socket.socket(socket.AF_UNIX)
conn.connect(str(args.socket_file))
conn.send('\x00'.join(args.targets).encode('utf8'))
