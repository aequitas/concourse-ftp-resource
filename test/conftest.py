import json
import socket
import stat
import subprocess
import sys

import pytest

# subdirectory in the ftp root to work on, vsftpd refused in writable root
DIRECTORY = 'test'

# default content for files to test
CONTENT = '123'

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
    return tmpdir.mkdir('ftproot')

@pytest.fixture
def work_dir(tmpdir):
    """Return temporary directory for output/input files."""
    return tmpdir.mkdir('work_dir')

@pytest.yield_fixture
def ftp_server(ftp_root, free_port):
    """Run FTP server on ftp_root.

    Returns uri to the ftp.
    """

    ftp_root.mkdir(DIRECTORY).chmod(stat.S_IWOTH | stat.S_IXOTH | stat.S_IROTH)

    cmd = [
        'vsftpd', '-olisten_port=' + str(free_port), '-oseccomp_sandbox=NO',
        '-oanon_root=' + str(ftp_root), '-oanon_upload_enable=YES',
        '-owrite_enable=YES', '-obackground=YES', '-oanon_other_write_enable=YES'
    ]
    process = subprocess.Popen(cmd)

    yield("ftp://localhost:{}/{}".format(free_port, DIRECTORY))

    process.terminate()

def cmd(cmd_name, source, args: list = [], version={}, params={}):
    """Wrap command interaction for easier use with python objects."""

    in_json = json.dumps({
        "source": source,
        "version": version,
        "params": params,
    })
    command = ['/opt/resource/' + cmd_name] + args
    output = subprocess.check_output(command,
        stderr=sys.stderr, input=bytes(in_json, 'utf-8'))

    return json.loads(output.decode())

def make_files(root, files, content='123'):
    """Create files in tmpdir root."""

    [root.join(DIRECTORY).join(f).write(content)for f in files]
