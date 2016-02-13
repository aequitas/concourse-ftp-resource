import json
import subprocess
import sys


def test_check_one_file(ftp_root, ftp_server):
    """Test if one uploaded file returns one version."""

    ftp_root.join('filename-0.0.0.tgz').write('')

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    in_json = json.dumps({
        "source": source
    })
    output = subprocess.check_output('/opt/resource/check',
        stderr=sys.stderr, input=bytes(in_json, 'utf-8'))

    result = json.loads(output.decode())

    assert result == [{"version": "0.0.0"}]

def test_check_multiple_files(ftp_root, ftp_server):
    """Test if multiple uploaded file return more versions."""

    ftp_root.join('filename-0.0.0.tgz').write('')
    ftp_root.join('filename-0.0.1.tgz').write('')

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    in_json = json.dumps({
        "source": source
    })
    output = subprocess.check_output('/opt/resource/check',
        stderr=sys.stderr, input=bytes(in_json, 'utf-8'))

    result = json.loads(output.decode())

    assert result == [{"version": "0.0.1"}], 'should only return most recent version'

def test_check_passing_version(ftp_root, ftp_server):
    """Test when a version is passed only new versions are returned."""

    ftp_root.join('filename-0.0.0.tgz').write('')
    ftp_root.join('filename-0.0.1.tgz').write('')
    ftp_root.join('filename-0.0.2.tgz').write('')
    ftp_root.join('filename-0.0.3.tgz').write('')

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    in_json = json.dumps({
        "source": source,
        "version": {
            "version": "0.0.1"
        }
    })
    output = subprocess.check_output('/opt/resource/check',
        stderr=sys.stderr, input=bytes(in_json, 'utf-8'))

    result = json.loads(output.decode())

    assert {"version": "0.0.2"} in result, 'new version should be in result'
    assert {"version": "0.0.3"} in result, 'new version should be in result'
    assert {"version": "0.0.0"} not in result, 'older version should not be in result'
    assert {"version": "0.0.1"} not in result, 'current version should not be in result'

def test_check_no_new_version(ftp_root, ftp_server):
    """When passing a version an no newer files return nothing."""

    ftp_root.join('filename-0.0.0.tgz').write('')
    ftp_root.join('filename-0.0.1.tgz').write('')

    source = {
        "uri": ftp_server,
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    in_json = json.dumps({
        "source": source,
        "version": {
            "version": "0.0.1"
        }
    })
    output = subprocess.check_output('/opt/resource/check',
        stderr=sys.stderr, input=bytes(in_json, 'utf-8'))

    result = json.loads(output.decode())

    assert result == []
