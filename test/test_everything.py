#!/usr/bin/python

import contextlib
from pathlib import Path
import subprocess
import time

@contextlib.contextmanager
def killing_Popen(*args, **kwargs):
    with subprocess.Popen(*args, **kwargs) as proc:
        try:
            yield
        finally:
            proc.kill()

def test_basics():
    target = Path('test.log')
    command = ['xargsd', '-s', 'test.sock', '--', 'echo']

    with killing_Popen(command, stdout=target.open('w')):
        time.sleep(0.2)

        target.write_text('')
        subprocess.check_call(['xargsd-cli', '-s', 'test.sock', 'a', 'b', 'c'])
        time.sleep(0.2)
        assert target.read_text() == 'a b c\n'
        subprocess.check_call(['xargsd-cli', '-s', 'test.sock', 'a', 'b', 'c'])
        time.sleep(0.2)
        assert target.read_text() == 'a b c\na b c\n'

def test_unique():
    target = Path('test.log')
    command = ['xargsd', '-u', '-s', 'test.sock', '--', 'echo']

    with killing_Popen(command, stdout=target.open('w')):
        time.sleep(0.2)

        target.write_text('')
        subprocess.check_call(['xargsd-cli', '-s', 'test.sock', 'a', 'a', 'b', 'c', 'b'])
        time.sleep(0.2)
        assert list(sorted(target.read_text().strip().split(' '))) == ['a', 'b', 'c']
