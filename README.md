# FTP Resource

Concourse resource to interact with FTP servers.

https://hub.docker.com/r/aequitas/ftp-resource/

## Deploying to Concourse

In your bosh deployment manifest, add to the `groundcrew.additional_resource_types` with the following:

```yaml
- image: docker:///aequitas/ftp-resource
  type: ftp
```

## Source Configuration

* `uri`: *Required.* The URI for the FTP server (including path).
    Example: `ftp://user:password@example.com/team/prod/`

* `regex`: *Required.* Regex to match filenames to. Supports capture groups. Requires at least one capture group named `version`. Other groups are added as `metadata`.

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
resources:
    - name: upload
      type: ftp
      source:
          uri: ftp://user:password@example.com:21/team/prod/
          regex: (?P<file>package_name-(?P<version>[0-9\.]+).*\.whl)

jobs:
    - name: test ftp
      plan:
          - task: build
            file: ci/build.yaml

          - put: upload
            params:
                file: build/dist/package_name-*.whl

```
