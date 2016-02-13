from conftest import cmd, make_files


def test_get_a_file(ftp_root, ftp_server, tmpdir):
    """Test if a file can be retrieved."""

    make_files(ftp_root, ['filename-0.0.0.tgz'])

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    result = cmd('in', source, [str(tmpdir)], version={"version": "0.0.0"})

    assert tmpdir.join('filename-0.0.0.tgz').read() == '123'
    assert result == {
        "version": {"version": "0.0.0"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.0.tgz"},
        ]
    }
