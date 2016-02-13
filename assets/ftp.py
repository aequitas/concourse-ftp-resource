#!/usr/bin/env python

import ftplib
import glob
import logging as log
import os
import re
import sys
from distutils.version import StrictVersion
from resource import Resource
from urllib.parse import urlparse

import ftputil


class UriSession(ftplib.FTP):
    """Ftputil session to accept a URI as contructor argument."""

    def __init__(self, uri):
        """Setup FTP session using provided URI."""

        ftplib.FTP.__init__(self)
        port = uri.port or 21
        self.connect(uri.hostname, port)
        if uri.username:
            self.login(uri.username, uri.password)
        else:
            self.login()

        log.debug('changing to: %s', uri.path)
        self.cwd(uri.path)

class FTPResource(Resource):
    """FTP resource implementation."""

    def context(self,
                uri: str,
                regex: str,
                version_key: str = 'version') -> str:
        """Provide context for commands to run in, takes 'source'."""

        self.regex = re.compile(regex)
        self.version_key = version_key

        return ftputil.FTPHost(urlparse(uri), session_factory=UriSession)

    def cmd_check(self, version: dict = {}) -> str:
        """Check for current or new version."""

        # get complete list of all versions
        versions = self._versions_to_output(self._matching_versions(self.ftp.listdir('.')))

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
        versions = self._matching_versions(self.ftp.listdir('.'))

        match_version = next(v for v in versions if v[self.version_key] == version[self.version_key])

        file_name = match_version['file']

        dest_file_path = os.path.join(dest_dir[0], file_name)

        self.ftp.download(file_name, dest_file_path)

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
            log.error('no files matched')

        src_file_path = glob_files[0]
        file_name = src_file_path.split('/')[-1]

        log.debug('uploading file: %s, as: %s', src_file_path, file_name)
        self.ftp.upload(src_file_path, file_name)

        if keep_versions:
            self._delete_old_versions(keep_versions)

        version = self.regex.match(file_name).groupdict()
        return self._version_to_output(version)

    def _delete_old_versions(self, keep_versions: int):
        """Delete old versions of file keeping up to specified amont."""
        old_versions = self._regex_matches(self.ftp.listdir('.'))[:-keep_versions]
        for delete_file_name in [v.group() for v in old_versions]:
            log.debug('deleting old version: %s', delete_file_name)
            self.ftp.remove(delete_file_name)


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
