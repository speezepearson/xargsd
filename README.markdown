Like `xargs`, but accepts arguments from arbitrary processes, and executes eagerly as long as there are arguments available.

That is to say, `xargsd [...] -- foobar`, when it receives arguments `a` and `b`, will execute `foobar a b`. If arguments `c` through `f` arrive while `foobar a b` is executing, then `foobar c d e f` will get run as soon as the first invocation finishes.

## Examples

(All these examples could easily be run in your shell, but then they wouldn't be doctest-able. Sorry!)

* A toy example, demonstrating the very basic functionality:

    ```python
    >>> import pexpect, subprocess
    >>> def sh(cmd): subprocess.check_call(cmd, shell=True)
    >>> p = pexpect.spawn('python -m xargsd --socket-file temp.sock -vvv -- echo')
    >>> _ = p.expect('xargsd is listening')
    >>> sh('python -m xargsd.client --socket-file temp.sock -- a')
    >>> _ = p.expect('a\r\n')
    >>> sh('python -m xargsd.client --socket-file temp.sock -- b c d')
    >>> _ = p.expect('b c d\r\n')

    ```

    (Note that the `INFO:` lines and the following ones are printed by `xargsd`, not the client.)

* A slightly-less-toy example, which demonstrates how commands are batched up while a previous command is executing:

    ```python
    >>> sh("""echo 'echo sleeping for "$@"; sleep "$@"' > /tmp/echo-and-sleep.sh""")
    >>> p = pexpect.spawn('python -m xargsd --socket-file temp.sock -vvv -- bash /tmp/echo-and-sleep.sh')
    >>> _ = p.expect('xargsd is listening')
    >>> sh('python -m xargsd.client --socket-file temp.sock -- 0.3')
    >>> sh('python -m xargsd.client --socket-file temp.sock -- 0.1 0.2')
    >>> sh('python -m xargsd.client --socket-file temp.sock -- 0.2 0.2')
    >>> _ = p.expect('sleeping for 0.3\r\n')  # TODO: might be a race condition?
    >>> _ = p.expect('sleeping for 0.1 0.2 0.2 0.2\r\n')

    ```

* A completely serious example, using `watchman` to run `xargsd.client` whenever a file (whose name matches some pattern) changes:

    ```python
    >>> if subprocess.call('which watchman >/dev/null 2>&1', shell=True) == 0:
    ...   import os
    ...   os.chdir(subprocess.check_output('mktemp --directory', shell=True).decode().strip())
    ...   sh('watchman watch .')
    ...   sh(r"watchman -- trigger . pytest -p '.*\.py$' -X -p '(^|.*/)\.' -- bash -c 'python -m xargsd.client --socket-file .xargsd-pytest.sock -- .'")
    ...   p = pexpect.spawn('python -m xargsd --unique --socket-file .xargsd-pytest.sock -vvv -- pytest --color=yes')
    ...   _ = p.expect('xargsd is listening')
    ...   sh("echo 'def test_that_passes(): assert True' > test_temp.py")
    ...   _ = p.expect('=== 1 passed in .* ===')
    ...

    ```

    Then save a `.py` file and watch the daemon execute `pytest .`
