# babycam

[![Build Status](https://travis-ci.org/luhn/babycam.svg?branch=master)](https://travis-ci.org/luhn/babycam)

Babycam is a simple command line script for watching files for changes and
emailing the appended content.  It can be used to keep an eye on error logs and
email you when an error pops up.  Babycam works with Python 2.6, 2.7, 3.2, 3.3,
and 3.4.

## Installing

babycam is not yet on PyPI, so install with:

```bash
pip install https://github.com/luhn/babycam/archive/v1.0.0.tar.gz
```

## Usage

```
usage: babycam [-h] [--host HOST] [--port PORT] [--ssl] [--tls] [--user USER]
               [--password PASSWORD] [--poll-frequency POLL_FREQUENCY]
               [--sender SENDER] [--data-dir DATA_DIR]
               recipient file [file ...]

Watch a file for changes.

positional arguments:
  recipient             The email address to send notices to.
  file                  The file(s) to watch.

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           The SMTP host.
  --port PORT           The SMTP port.
  --ssl                 Use SMTP over SSL.
  --tls                 Upgrade to TLS once connected.
  --user USER           The SMTP username.
  --password PASSWORD   The SMTP password.
  --poll-frequency POLL_FREQUENCY
                        The frequency (in seconds) to poll the files.
  --sender SENDER       The email address to use as a from address. Defaults
                        to {user}@{hostname}
  --data-dir DATA_DIR   The directory to store application data. Defaults to
                        the directory of the file.
```

For example:

```bash
babycam \
	--host mailtrap.io \
	--port 465 \
	--tls \
	--user 29958a97d6cf2a800 \
	--password db61946a6311c3 \
	--poll-frequency 1 \
 	test@example.com \
	file1.txt file2.txt
```

If you append content to `file2.txt`, you'll get an email like the following:

```
The file /Users/Luhn/Code/babycam/file2.txt has changed!

Timestamp:  2015-02-16T15:02:25.152958

See attached file for details.
```

Attached to this email is a text file of the appended content.

Babycam makes a small file called `.[filename].babycam` in the same directory
as the watched file, in order to keep track of changes, so it must have write
permissions to that directory.  If this is not feasable, you can change the
directory babycam writes to using the `--data-dir` argument.

If you wish to truncate a file Babycam is watching, be sure to delete the
corresponding `.babycam` file, otherwise addendums to the truncated file will
not be detected.

## Daemonizing

It's often desirable to run Babycam as a daemon.  To achieve this, use software
such as [Supervisor](http://supervisord.org/).

## Roadmap

* Add support for `inotify` so we can avoid the overhead of polling.
* Better behavior when the file is modified rather than being appended.
  * Support truncating files without having to delete the `.babycam` file.
