import stat

from conftest import cmd


def test_put_a_file(ftp_root, ftp_server, tmpdir):
    """Test if a file can be stored."""

    tmpdir.join('filename-0.0.0.tgz').write('123')
    ftp_root.mkdir('test').chmod(stat.S_IWOTH | stat.S_IXOTH | stat.S_IROTH)

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    params = {
        "file": "*.tgz"
    }

    result = cmd('out', source, [str(tmpdir)], params=params)

    assert ftp_root.join('test').join('filename-0.0.0.tgz').read() == '123'
    assert result == {
        "version": {"version": "0.0.0"},
        "metadata": [
            {"name": "file", "value": "filename-0.0.0.tgz"},
        ]
    }
