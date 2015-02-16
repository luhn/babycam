import os
from collections import namedtuple
from base64 import urlsafe_b64encode as b64encode
from mock import MagicMock

from babycam import check, generate_email_text, send_email


def _generate_filenames():
    """
    Create a random file name and the corresponding .babycam file.

    """
    name = b64encode(os.urandom(12)).decode('ascii')
    return (
        '/tmp/{0}.test'.format(name),
        '/tmp/.{0}.test.babycam'.format(name),
    )


def test_check_new_file():
    """
    Check a file that we've never seen before.  Should write length to babycam
    file and return a nullstring as the new content.

    """
    fn, babycam_file = _generate_filenames()

    with open(fn, 'w') as fh:
        fh.write('foobar')

    assert check(fn) == ''

    with open(babycam_file) as fh:
        assert fh.read().strip() == '6'


def test_check():
    """
    Check a file that we've been monitoring.  First, there's nothing new, then
    we append something.

    """
    fn, babycam_file = _generate_filenames()

    with open(fn, 'w') as fh:
        fh.write('foobar\n')

    with open(babycam_file, 'w') as fh:
        fh.write('7\n')

    assert check(fn) == ''

    # Now append something and test again
    with open(fn, 'a') as fh:
        fh.write('buzz')

    assert check(fn) == 'buzz'

    with open(babycam_file) as fh:
        assert fh.read().strip() == '11'


def test_generate_email_text():
    fn, _ = _generate_filenames()
    subject, text = generate_email_text(fn)
    assert subject == 'File changed: {0}'.format(fn)
    lines = text.split('\n')
    assert lines[0] == 'The file {0} has changed!'.format(fn)
    assert lines[2].startswith('Timestamp: ')


def test_send_email():
    """
    We won't test the content of the message, just that it sends without
    errors.  Content should be checked manually.

    """
    args = namedtuple('Arguments', [
        'sender', 'recipient',
    ])(
        'sender@example.com',
        'test@example.com',
    )
    conn = MagicMock()
    conn.sendmail = MagicMock()

    fn, _ = _generate_filenames()
    subject, text = generate_email_text(fn)
    send_email(conn, args, subject, text, 'Changes in file.')
    assert conn.sendmail.call_count == 1
    args, kwargs = conn.sendmail.call_args
    assert args[0] == 'sender@example.com'
    assert args[1] == 'test@example.com'
