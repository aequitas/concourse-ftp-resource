from conftest import cmd, make_files


def test_get_a_file(ftp_root, ftp_server, work_dir):
    """Test if a file can be retrieved."""

    make_files(ftp_root, ['filename-0.0.0.tgz'])

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    result = cmd('in', source, [str(work_dir)], version={"version": "0.0.0"})

    assert work_dir.join('filename-0.0.0.tgz').read() == '123'
    assert result == {
        "version": {"version": "0.0.0"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.0.tgz"},
        ]
    }
