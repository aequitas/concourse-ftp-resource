import glob
import json
import os
import tempfile

from conftest import CONTENT, DIRECTORY, cmd, make_files


def test_put_a_file(ftp_root, ftp_server, work_dir):
    """Test if a file can be stored."""

    work_dir.join('filename-0.0.0.tgz').write(CONTENT)

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    result = cmd('out', source, [str(work_dir)])

    assert ftp_root.join(DIRECTORY).join('filename-0.0.0.tgz').read() == CONTENT
    assert result == {
        "version": {"version": "0.0.0"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.0.tgz"},
        ]
    }

def test_put_a_file_glob(ftp_root, ftp_server, work_dir):
    """Test if only specific files are uploaded."""

    work_dir.join('filename-0.0.0.tgz').write(CONTENT)
    work_dir.join('otherfilename-0.0.0.tgz').write(CONTENT)

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    params = {
        "file": "filename-*.tgz"
    }

    result = cmd('out', source, [str(work_dir)], params=params)

    assert ftp_root.join(DIRECTORY).join('filename-0.0.0.tgz').read() == CONTENT
    assert result == {
        "version": {"version": "0.0.0"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.0.tgz"},
        ]
    }

def test_delete_old(ftp_root, ftp_server, work_dir):
    """Test if old versions of files will be deleted."""

    # create file to upload
    work_dir.join('filename-0.0.4.tgz').write(CONTENT)
    make_files(ftp_root, [
        'filename-0.0.0.tgz', 'filename-0.0.1.tgz', 'filename-0.0.2.tgz', 'filename-0.0.3.tgz'
    ])

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    params = {
        'keep_versions': 3
    }

    result = cmd('out', source, [str(work_dir)], params=params)

    # three latests versions should be kept
    assert ftp_root.join(DIRECTORY).join('filename-0.0.2.tgz').read() == CONTENT
    assert ftp_root.join(DIRECTORY).join('filename-0.0.3.tgz').read() == CONTENT
    assert ftp_root.join(DIRECTORY).join('filename-0.0.4.tgz').read() == CONTENT
    # old files should be deleted
    assert not ftp_root.join(DIRECTORY).join('filename-0.0.0.tgz').exists()
    assert not ftp_root.join(DIRECTORY).join('filename-0.0.1.tgz').exists()

    assert result == {
        "version": {"version": "0.0.4"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.4.tgz"},
        ]
    }

def test_delete_old_few(ftp_root, ftp_server, work_dir):
    """Test if to few files are not deleted."""

    # create file to upload
    work_dir.join('filename-0.0.4.tgz').write(CONTENT)
    make_files(ftp_root, ['filename-0.0.3.tgz'])

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    params = {
        'keep_versions': 3
    }

    result = cmd('out', source, [str(work_dir)], params=params)

    # three latests versions should be kept
    assert ftp_root.join(DIRECTORY).join('filename-0.0.3.tgz').read() == CONTENT
    assert ftp_root.join(DIRECTORY).join('filename-0.0.4.tgz').read() == CONTENT

    assert result == {
        "version": {"version": "0.0.4"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.4.tgz"},
        ]
    }

def test_delete_old_sorting(ftp_root, ftp_server, work_dir):
    """Test if natural sorting is used when deleting."""

    # create file to upload
    work_dir.join('filename-0.0.14.tgz').write(CONTENT)
    make_files(ftp_root, [
        'filename-0.0.0.tgz',
        'filename-0.0.1.tgz',
        'filename-0.0.2.tgz',
        'filename-0.0.3.tgz',
        'filename-0.0.10.tgz',
        'filename-0.0.11.tgz',
        'filename-0.0.12.tgz',
        'filename-0.0.13.tgz',
    ])

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    params = {
        'keep_versions': 3
    }

    result = cmd('out', source, [str(work_dir)], params=params)

    # old files should be deleted
    assert not ftp_root.join(DIRECTORY).join('filename-0.0.0.tgz').exists()
    assert not ftp_root.join(DIRECTORY).join('filename-0.0.1.tgz').exists()
    assert not ftp_root.join(DIRECTORY).join('filename-0.0.2.tgz').exists()
    assert not ftp_root.join(DIRECTORY).join('filename-0.0.3.tgz').exists()
    assert not ftp_root.join(DIRECTORY).join('filename-0.0.10.tgz').exists()
    assert not ftp_root.join(DIRECTORY).join('filename-0.0.11.tgz').exists()
    # three latests versions should be kept
    assert ftp_root.join(DIRECTORY).join('filename-0.0.12.tgz').read() == CONTENT
    assert ftp_root.join(DIRECTORY).join('filename-0.0.13.tgz').read() == CONTENT
    assert ftp_root.join(DIRECTORY).join('filename-0.0.14.tgz').read() == CONTENT

    assert result == {
        "version": {"version": "0.0.14"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.14.tgz"},
        ]
    }

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

def test_put_a_file_ssl(ftp_root, ftp_server, work_dir):
    """Test if a file can be stored."""

    work_dir.join('filename-0.0.0.tgz').write(CONTENT)

    source = {
        "uri": ftp_server.replace('ftp', 'ftps'),
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    result = cmd('out', source, [str(work_dir)])

    assert ftp_root.join(DIRECTORY).join('filename-0.0.0.tgz').read() == CONTENT
    assert result == {
        "version": {"version": "0.0.0"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.0.tgz"},
        ]
    }
