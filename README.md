# FTP Resource

Concourse resource to interact with FTP servers.

https://hub.docker.com/r/aequitas/ftp-resource/

## Recent changes

- 06-2018: Handle missing previous versions (https://github.com/aequitas/concourse-ftp-resource/issues/8)
- 01-2018: added support for semver versions.

## Deploying to Concourse

No changes are necessary to BOSH configuration. However, you must define the FTP resource in a `resource_types` as can be seen in the below example pipeline.

## Source Configuration

* `uri`: *Required.* The URI for the FTP server (including path).
    Example: `ftp://user:password@example.com/team/prod/`

* `regex`: *Required.* Python regex to match filenames to. Supports capture groups. Requires at least one capture group named `version`. Other groups are added as `metadata`.

* `version_key`: *Optional* Alternative key to be used for the `version` capture group (default `version`).

* `debug`: *Optional* Set debug logging of scripts, takes boolean (default `true`).

## Behavior

### `check`: Return list of file versions.

Will request a list of files from the `uri` and filter on matching `regex` extracting the `version_key` and returning list of versions captured groups.

### `in`: Retrieve file matching `version` from ftp.

Uses the `regex` to compose a list of files and versions, will return the one file that matches the `version` provided in `params`.

#### Parameters

* `version`: *Required* The version to return (will be matched against the `version` regex capture group).

### `out`: Upload file(s) matching `file` glob to ftp.

Uploads a file(s) glob matching `file` to the ftp directory specified by `uri`.

* `file`: Glob used to determine files to upload from src dir (default `*`).

* `keep_versions`: If specified determined the amount of files to keep, deleting the old versions (default null). Requires a regex capture group named `file` to work.

#### Parameters

* `file`: *Required.* Glob pattern to specify which files need to be uploaded.

## Example pipeline

```yaml
resource_types:
  - name: ftp
    type: docker-image
    source:
      repository: aequitas/ftp-resource

resources:
  - name: ftpupload
    type: ftp
    source:
      regex: (?P<file>test(?P<version>[0-9\.]+).*\.txt)
      uri: ftp://user:password@example.com:21/team/prod/

jobs:
  - name: testftp
    plan:
      - task: touchfile
        config:
          platform: linux
          run:
            path: sh
            args:
            - -exc
            - |
              touch test/test1.txt
          outputs:
          - name: test
      - put: ftpupload
        params:
          file: test/test1.txt

```


