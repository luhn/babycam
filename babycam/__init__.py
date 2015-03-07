import argparse
import time
import os.path
import smtplib
import socket
import getpass
from datetime import datetime as DateTime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from contextlib import contextmanager


def main():
    default_sender = '{0}@{1}'.format(
        getpass.getuser(),
        socket.getfqdn(),
    )

    parser = argparse.ArgumentParser(
        description='Watch a file for changes.',
    )
    parser.add_argument(
        'recipient',
        help='The email address to send notices to.',
    )
    parser.add_argument(
        'file',
        nargs='+',
        help='The file(s) to watch.',
    )
    parser.add_argument('--host', default='localhost', help='The SMTP host.')
    parser.add_argument('--port', type=int, default=25, help='The SMTP port.')
    parser.add_argument(
        '--ssl', action='store_const', const=True, default=False,
        help='Use SMTP over SSL.',
    )
    parser.add_argument(
        '--tls', action='store_const', const=True, default=False,
        help='Upgrade to TLS once connected.',
    )
    parser.add_argument('--user', help='The SMTP username.')
    parser.add_argument('--password', help='The SMTP password.')
    parser.add_argument(
        '--poll-frequency', type=int, default=15,
        help='The frequency (in seconds) to poll the files.',
    )
    parser.add_argument(
        '--sender',
        default=default_sender,
        help=(
            'The email address to use as a from address.  Defaults to ' +
            '{user}@{hostname}'
        ),
    )
    parser.add_argument(
        '--data-dir',
        help=(
            'The directory to store application data.  Defaults to the ' +
            'directory of the file.'
        ),
    )
    args = parser.parse_args()

    # Quit check the SMTP connection
    with smtp_connect(args) as conn:
        conn.verify('test@example.com')

    # Start polling
    while True:
        for filename in args.file:
            new_content = check(filename, data_dir=args.data_dir)
            if new_content:
                subject, text = generate_email_text(filename)
                with smtp_connect(args) as conn:
                    send_email(conn, args, subject, text, new_content)

        time.sleep(args.poll_frequency)


def check(filename, data_dir=None):
    """
    Check the file for any new content, and return it.  Stores the length of
    the file, so we know what's been added.

    """
    head, tail = os.path.split(filename)
    if data_dir is None:
        data_dir = head

    data_file = os.path.join(
        data_dir,
        '.{0}.babycam'.format(tail.lstrip('.')),
    )

    # Get the length of the file.
    if os.path.exists(data_file):
        with open(data_file) as fh:
            old_length = int(fh.read().strip())
    else:
        # Special case if the file does not yet exist
        old_length = None

    # Check the file length, get any addendums
    with open(filename) as fh:
        if old_length is None:
            # If we've never looked at it before, we find how long it is and
            # say there's nothing new.
            fh.seek(0, 2)
            new_length = fh.tell()
            new_content = ''
        else:
            fh.seek(old_length)
            new_content = fh.read()
            new_length = old_length + len(new_content)

    # Store the new length of the file
    if new_length != old_length:
        with open(data_file, 'w') as fh:
            fh.write(str(new_length))
            fh.write('\n')

    return new_content


def generate_email_text(filename):
    """
    Generate some text for the email.  Returns two-tuple of subject and text.

    """
    absolute = os.path.abspath(filename)
    hostname = socket.getfqdn()
    return (
        'File changed: {0}'.format(absolute),
        (
            'The file {0} has changed!\n\n'.format(absolute) +
            'Timestamp:  {0}\n'.format(DateTime.now().isoformat()) +
            'Hostname:  {0}\n\n'.format(hostname) +
            'See attached file for details.'
        ),
    )


def send_email(conn, args, subject, text, changes):
    """
    Send the file.

    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = args.sender
    msg['To'] = args.recipient

    attach = MIMEText(changes)
    attach.add_header(
        'Content-Disposition',
        'attachment',
        filename='changes.txt',
    )
    msg.attach(attach)

    msg.attach(MIMEText(text))

    conn.sendmail(args.sender, args.recipient, msg.as_string())


@contextmanager
def smtp_connect(args):
    """
    A context manager that opens a SMTP connection.  Binds
    :class:`smtplib.SMTP` or :class:`smtplib.SMTP_SSL` to the target.

    """
    SMTP = smtplib.SMTP_SSL if args.ssl else smtplib.SMTP
    conn = SMTP(args.host, args.port)
    if args.tls:
        conn.starttls()
    if args.user:
        conn.login(args.user, args.password)
    yield conn
    conn.quit()
