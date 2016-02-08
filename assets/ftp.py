#!/usr/bin/env python

import glob
import json
import logging
import os
import re
import sys
from urlparse import urlparse

import ftputil
from common import (UriSession, matching_versions, version_to_output,
                    versions_to_output)

params = json.loads(sys.stdin.read())
command = os.path.basename(__file__)

if params['source'].get('debug', True):
    logging.basicConfig(level=logging.DEBUG)

logging.debug('source: %s', source)
logging.debug('params: %s', params)
logging.debug('argv: %s', sys.argv)

# source parameters
uri = urlparse(params['source']['uri'])
regex = re.compile(params['source']['regex'])
version_key = params['source'].get('version_key', 'version')

if command == 'check':
    with ftputil.FTPHost(uri, session_factory=UriSession) as ftp:
        # get matching version from file list
        versions = matching_versions(ftp.listdir('.'), regex)

    output = versions_to_output(versions, version_key)

elif command == 'in':
    dest_dir = sys.argv[1]
    version = params['version']['version']

    with ftputil.FTPHost(uri, session_factory=UriSession) as ftp:
        # get matching version from file list
        versions = matching_versions(ftp.listdir('.'), regex)

        match_version = next(v for v in versions if v[version_key] == version)

        file_name = match_version['file']
        dest_file_path = os.path.join(dest_dir, file_name)

        ftp.download(file_name, dest_file_path)

    output = version_to_output(match_version, version_key)

elif command == 'out':
    src_dir = sys.argv[1]
    file_glob = params['params']['file']

    src_file_path = glob.glob(os.path.join(src_dir, file_glob))[0]
    file_name = src_file_path.split('/')[-1]

    with ftputil.FTPHost(uri, session_factory=UriSession) as ftp:
        ftp.upload(src_file_path, file_name)

    version = regex.match(file_name).groupdict()
    output = version_to_output(version, version_key)

print(json.dumps(output))
