import json
import subprocess
import sys


def test_check_one_file(uploaded_file, ftp_server):
    """Test if one uploaded file returns one version."""
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

    assert {"version": "0.0.0"} in result

def test_check_multiple_files(uploaded_files, ftp_server):
    """Test if multiple uploaded file return more versions."""
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

    assert {"version": "0.0.0"} in result
    assert {"version": "0.0.1"} in result
