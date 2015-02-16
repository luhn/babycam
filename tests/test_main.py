import os
from collections import namedtuple
from base64 import urlsafe_b64encode as b64encode

from babycam import check, generate_email_text, send_email


def _generate_filenames():
    """
    Create a random file name and the corresponding .babycam file.

    """
    name = b64encode(os.urandom(12)).decode('ascii')
    return (
        '/tmp/{}.test'.format(name),
        '/tmp/.{}.test.babycam'.format(name),
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
    assert subject == 'File changed: {}'.format(fn)
    lines = text.split('\n')
    assert lines[0] == 'The file {} has changed!'.format(fn)
    assert lines[2].startswith('Timestamp: ')


def test_send_email():
    """
    We won't test the content of the message, just that it sends without
    errors.  Content should be checked manually.

    """
    args = namedtuple('Arguments', [
        'sender', 'recipient', 'user', 'password', 'ssl', 'tls', 'host',
        'port',
    ])(
        'sender@example.com',
        'test@example.com',
        '29958a97d6cf2a800',
        'db61946a6311c3',
        False,
        True,
        'mailtrap.io',
        465,
    )

    fn, _ = _generate_filenames()
    subject, text = generate_email_text(fn)
    send_email(args, subject, text, 'Changes in file.')