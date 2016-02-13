import json
import socket
import subprocess
import sys

import pytest


@pytest.fixture
def free_port():
    """temporary bind to socket 0 to get a free port assigned by the OS."""
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

@pytest.fixture
def ftp_root(tmpdir):
    """Return temporary ftp root directory."""
    return tmpdir

@pytest.yield_fixture
def ftp_server(ftp_root, free_port):
    """Run FTP server on ftp_root.

    Returns uri to the ftp.
    """

    cmd = [
        'vsftpd', '-olisten_port=' + str(free_port), '-oseccomp_sandbox=NO',
        '-oanon_root=' + str(ftp_root), '-oanon_upload_enable=YES',
        '-owrite_enable=YES', '-obackground=YES',
    ]
    process = subprocess.Popen(cmd)
    yield("ftp://localhost:{}".format(free_port))
    process.terminate()

def cmd(cmd_name, source, args=[], version={}, params={}):
    """Wrap command interaction for easier use with python objects."""

    in_json = json.dumps({
        "source": source,
        "version": version,
        "params": params,
    })
    output = subprocess.check_output('/opt/resource/check',
        stderr=sys.stderr, input=bytes(in_json, 'utf-8'))

    return json.loads(output.decode())
