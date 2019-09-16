import argparse
import asyncio
import functools
import logging
import socket
from pathlib import Path
from typing import Sequence

parser = argparse.ArgumentParser(description='Run a command on arguments as they arrive over a socket.')
parser.add_argument('-s', '--socket-file', type=Path, required=True)
parser.add_argument('-u', '--unique', action='store_true')
parser.add_argument('-v', '--verbose', action='count', default=0)
parser.add_argument('command', nargs='+')

class EnqueueingProtocol(asyncio.protocols.Protocol):
    def __init__(self, queue: 'asyncio.Queue[str]') -> None:
        self.queue = queue
    def data_received(self, data) -> None:
        for line in data.decode('utf8').split('\x00'):
            self.queue.put_nowait(line)

async def execute_command_on_targets(command: Sequence[str],
                                     queue: 'asyncio.Queue[str]',
                                     unique: bool = False,
                                     ) -> None:
    while True:
        targets = [await queue.get()]
        while queue.qsize() > 0: targets.append(queue.get_nowait())
        if unique: targets = sorted(set(targets))
        full_command = [*command, *targets]
        logging.info(f'executing {full_command}')
        proc = await asyncio.create_subprocess_exec(*full_command)
        await proc.communicate()
        logging.debug(f'finished executing {full_command}: status {proc.returncode}')

async def run_server(
    command: Sequence[str],
    socket_file: Path,
    unique: bool = False,
):
    queue: 'asyncio.Queue[str]' = asyncio.Queue()
    server = await asyncio.get_event_loop().create_unix_server(
        (lambda: EnqueueingProtocol(queue)),
        socket_file)
    logging.info('xargsd is listening on %s ...', socket_file)
    await asyncio.gather(
        server.serve_forever(),
        execute_command_on_targets(command, queue))

@functools.wraps(run_server, assigned=['__annotations__'])
def run_server_sync(*args, **kwargs):
    '''Wrapper around `run_server` to run the coroutine synchronously.'''
    asyncio.get_event_loop().run_until_complete(run_server(*args, **kwargs))


def main():
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING if args.verbose==0 else logging.INFO if args.verbose==1 else logging.DEBUG)
    run_server_sync(
        command=args.command,
        socket_file=args.socket_file,
        unique=args.unique,
    )
