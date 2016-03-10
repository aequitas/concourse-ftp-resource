#!/usr/bin/env python3

import ftplib
import glob
import json
import logging as log
import os
import re
import ssl
import sys
import tempfile
from distutils.version import StrictVersion
from urllib.parse import urlparse

from ftputil.stat import UnixParser


class UriSession(ftplib.FTP):
    """Ftputil session to accept a URI as contructor argument."""
    ssl_version = ssl.PROTOCOL_SSLv23

    def __init__(self, uri):
        """Setup FTP session using provided URI."""

        if uri.scheme == 'ftps':
            ftplib.FTP_TLS.__init__(self)
        else:
            ftplib.FTP.__init__(self)
        port = uri.port or 21
        self.connect(uri.hostname, port)
        if uri.username:
            self.login(uri.username, uri.password)
        else:
            self.login()

        log.debug('changing to: %s', uri.path)
        self.cwd(uri.path)

class FTPResource:
    """FTP resource implementation."""

    parser = UnixParser()

    def run(self, command_name: str, json_data: str, command_argument: str):
        """Parse input/arguments, perform requested command return output."""

        with tempfile.NamedTemporaryFile(delete=False, prefix=command_name + '-') as f:
            f.write(bytes(json_data, 'utf-8'))

        data = json.loads(json_data)

        # allow debug logging to console for tests
        if os.environ.get('RESOURCE_DEBUG', False) or data.get('source', {}).get('debug', False):
            log.basicConfig(level=log.DEBUG)
        else:
            logfile = tempfile.NamedTemporaryFile(delete=False, prefix='log')
            log.basicConfig(level=log.DEBUG, filename=logfile.name)
            stderr = log.StreamHandler()
            stderr.setLevel(log.INFO)
            log.getLogger().addHandler(stderr)

        log.debug('command: %s', command_name)
        log.debug('input: %s', data)
        log.debug('args: %s', command_argument)

        self.regex = re.compile(data['source']['regex'])
        self.version_key = data['source'].get('version_key', 'version')

        self.connect(urlparse(data['source']['uri']))

        if command_name == 'check':
            output = self.cmd_check(version=data.get('version', {}))
        elif command_name == 'in':
            output = self.cmd_in(command_argument, version=data.get('version'))
        elif command_name == 'out':
            output = self.cmd_out(command_argument, **data.get('params', {}))

        self.close()

        return json.dumps(output)

    def connect(self, uri):
        """Connect to FTP server."""

        if uri.scheme == 'ftps':
            self.ftp = ftplib.FTP_TLS()
        else:
            self.ftp = ftplib.FTP()

        log.info('connecting to ftp server')
        port = uri.port or 21
        self.ftp.connect(uri.hostname, port)

        log.info('logging in')
        if uri.username:
            self.ftp.login(uri.username, uri.password)
        else:
            self.ftp.login()

        log.info('changing to directory %s', uri.path)
        self.ftp.cwd(uri.path)

    def close(self):
        """Gracefully close ftp connection."""

        try:
            self.ftp.quit()
        except EOFError:
            self.ftp.close()

    def listdir(self):
        """List current directory contents."""

        dirlist = []
        self.ftp.dir(dirlist.append)

        return [self.parser.parse_line(d)._st_name for d in dirlist]

    def cmd_check(self, version: dict = {}) -> str:
        """Check for current or new version."""

        # get complete list of all versions
        versions = self._versions_to_output(self._matching_versions(self.listdir()))

        if not versions:
            log.warning('no versions found')
            return []

        # if version is specified get newer versions
        if version:
            current_version = version
            new_versions = versions[versions.index(current_version):]
            new_versions.pop(0)
        else:
            # otherwise only get the current version
            new_versions = [versions[-1]]

        return new_versions

    def cmd_in(self,
               dest_dir: [str],
               version: dict) -> str:
        """Retrieve file matching version into dest_dir.."""
        # get matching version from file list
        versions = self._matching_versions(self.listdir())

        match_version = next(v for v in versions if v[self.version_key] == version[self.version_key])

        file_name = match_version['file']

        dest_file_path = os.path.join(dest_dir[0], file_name)

        with open(dest_file_path, 'wb') as f:
            self.ftp.retrbinary('RETR ' + file_name, callback=f.write)

        return self._version_to_output(match_version)

    def cmd_out(self,
                src_dir: [str],
                file: str = '*',
                keep_versions: int = None) -> str:
        """Upload all files in src_dir matching glob."""
        file_glob = file
        glob_files = glob.glob(os.path.join(src_dir[0], file_glob))
        log.debug('glob matched files: %s', glob_files)
        if not glob_files:
            raise Exception('no files matched {} in {}'.format(file_glob, src_dir[0]))

        src_file_path = glob_files[0]
        file_name = src_file_path.split('/')[-1]

        log.info('uploading file: %s, as: %s', src_file_path, file_name)
        with open(src_file_path, 'rb') as f:
            try:
                self.ftp.storbinary('STOR ' + file_name, f)
            except EOFError:
                log.warning('connection closed during/after transfer')

        if keep_versions:
            self._delete_old_versions(keep_versions)

        version = self.regex.match(file_name).groupdict()
        return self._version_to_output(version)

    def _delete_old_versions(self, keep_versions: int):
        """Delete old versions of file keeping up to specified amont."""
        versions = [m.groupdict() for m in self._regex_matches(self.listdir())]
        versions.sort(key=lambda x: StrictVersion(x[self.version_key]))

        old_versions = versions[:-keep_versions]

        for delete_file_name in [v['file'] for v in old_versions]:
            log.debug('deleting old version: %s', delete_file_name)
            self.ftp.delete(delete_file_name)


    def _versions_to_output(self, versions: [str]):
        """Convert list of k/v dicts into list of `version` output."""
        versions.sort(key=lambda x: StrictVersion(x[self.version_key]))
        output = [{self.version_key: version[self.version_key]} for version in versions]

        return output

    def _regex_matches(self, file_list: [str]):
        """Return list of matched regex objects for matching elements in file_list."""
        return [m for m in [self.regex.match(f) for f in file_list] if m]

    def _matching_versions(self, file_list: [str]):
        """Return dict of matched regex groups for matching elements in file_list."""
        return [m.groupdict() for m in self._regex_matches(file_list)]

    def _version_to_output(self, version: str):
        """Convert single k/v version dict into `version`/`metadata` output."""

        output = {'version': {self.version_key: version[self.version_key]}}
        if len(version.keys()) > 1:
            output.update({'metadata': [
                {"name": k, "value": v} for k, v in version.items() if not k == self.version_key
            ]})

        return output

print(FTPResource().run(os.path.basename(__file__), sys.stdin.read(), sys.argv[1:]))
