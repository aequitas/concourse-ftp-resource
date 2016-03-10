import glob
import json
import os
import tempfile

from conftest import CONTENT, cmd


def test_logging(ftp_root, ftp_server, work_dir, capfd):
    """Test if INFO and up is logged to stderr as well."""

    work_dir.join('filename-0.0.0.tgz').write(CONTENT)

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    cmd('out', source, [str(work_dir)])

    # test if INFO messages are logged
    assert 'uploading file:' in capfd.readouterr()[1]

def test_log_input(ftp_root, ftp_server, work_dir, capfd):
    """Test if JSON input is logged to file for easy replay."""

    work_dir.join('log_input-0.0.0.tgz').write(CONTENT)

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>log_input-(?P<version>.*).tgz)"
    }

    cmd('out', source, [str(work_dir)])

    in_files = sorted(glob.glob(os.path.join(tempfile.tempdir, 'in-*')), key=os.path.getmtime)
    assert in_files

    with open(in_files[-1]) as f:
        assert set(json.loads(f.read()).keys()) == {"params", "source", "version"}
