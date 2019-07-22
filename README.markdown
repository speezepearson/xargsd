Like `xargs`, but accepts arguments from arbitrary processes, and executes eagerly as long as there are arguments available.

That is to say, `xargsd [...] -- foobar`, when it receives arguments `a` and `b`, will execute `foobar a b`. If arguments `c` through `f` arrive while `foobar a b` is executing, then `foobar c d e f` will get run as soon as the first invocation finishes.

## Examples
* A toy example, demonstrating the very basic functionality:

    ```bash
    $ python -m xargsd --socket-file temp.sock -vvv -- echo &
    [1] 14917
    $ submit() { python -m xargsd.client --socket-file temp.sock -- "$@"; }
    $ submit a
    INFO:root:executing ['echo', 'a']
    a
    $ submit b c d
    INFO:root:executing ['echo', 'b', 'c', 'd']
    b c d
    ```

    (Note that the `INFO:` lines and the following ones are printed by `xargsd`, not the client.)

* A slightly-less-toy example, which demonstrates how commands are batched up while a previous command is executing:

    ```bash
    $ echo 'date; sleep "$@"' > date-and-sleep.sh
    $ python -m xargsd --socket-file temp.sock -vvv -- bash date-and-sleep.sh &
    [4] 15714
    $ submit() { echo "submitting $@"; python -m xargsd.client --socket-file temp.sock -- "$@"; }
    $ submit 1; sleep 0.1; submit 0.99; sleep 0.1; submit 1.01; sleep 3
    submitting 1
    INFO:root:executing ['bash', 'date-and-sleep.sh', '1']
    Sun May 12 09:53:13 PDT 2019
    submitting 0.99
    submitting 1.01
    DEBUG:root:finished executing ['bash', 'date-and-sleep.sh', '1']: status 0
    INFO:root:executing ['bash', 'date-and-sleep.sh', '0.99', '1.01']
    Sun May 12 09:53:14 PDT 2019
    DEBUG:root:finished executing ['bash', 'date-and-sleep.sh', '0.99', '1.01']: status 0
    ```

* A completely serious example, using `watchman` to run `xargsd.client` whenever a file (whose name matches some pattern) changes:

    ```bash
    $ watchman watch .
    $ watchman -- trigger . pytest -p '.*\.py$' -X -p '(^|.*/)\.' -- bash -c 'python -m xargsd.client --socket-file .xargsd-pytest.sock -- .'
    $ python -m xargsd --unique --socket-file .xargsd-pytest.sock -vvv -- pytest --color=yes
    ```

    Then save a `.py` file and watch the daemon execute `pytest .`
