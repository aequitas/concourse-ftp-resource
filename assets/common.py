from distutils.version import StrictVersion
import ftplib

def matching_versions(file_list, regex):
    """Return dict of matched regex groups for matching elements in file_list."""
    return [m.groupdict() for m in [regex.match(f) for f in file_list] if m]

def versions_to_output(versions, version_key):
    """Convert list of k/v dicts into list of `version` output."""
    versions.sort(key=lambda x: StrictVersion(x[version_key]))
    output = [{version_key: version[version_key]} for version in versions]

    return output

def version_to_output(version, version_key):
    """Convert single k/v version dict into `version`/`metadata` output."""

    output = {'version': {version_key: version[version_key]}}
    if len(version.keys()) > 1:
        output.update({'metadata': [
            {"name": k, "value": v} for k, v in version.items() if not k == version_key
        ]})

    return output


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

        self.cwd(uri.path)
