import json
import subprocess
import sys


def test_check_one_file(uploaded_file):
    source = {
        "uri": uploaded_file['ftp_uri'],
        "regex": "(?P<file>filename-(?P<version>.*).tgz)"
    }

    expected = [{
        "version": "0.0.0"
    }]

    in_json = json.dumps({
        "source": source
    })
    output = subprocess.check_output('/opt/resource/check',
        stderr=sys.stderr, input=bytes(in_json, 'utf-8'))
    print('out', output)
    result = json.loads(output.decode())

    assert result == expected
