#!/bin/sh

export PATH=/usr/local/bin/:${PATH}

set -e -u

set -o pipefail

resource_dir=/opt/resource

# make sure backend processes (vsftpd) are killed on exit
trap 'pkill vsftpd' EXIT

# print out test running
run() {
  export TMPDIR=$(mktemp -d ${TMPDIR_ROOT}/ftp-tests.XXXXXX)

  echo -e 'running \e[33m'"$@"$'\e[0m...'
  eval "$@" 2>&1 | sed -e 's/^/  /g'
  echo ""
}

# pass ftp uri as param into check command
check_uri() {
  jq -n "{
    source: {
      uri: $(echo $1 | jq -R .),
      regex: $(echo $2 | jq -R .)
    }
  }" | ${resource_dir}/check | tee /dev/stderr
}

get_uri() {
  jq -n "{
    source: {
      uri: $(echo $1 | jq -R .),
      template: $(echo $2 | jq -R .)
    },
    version: {
      ref: $(echo $3 | jq -R .)
    }
  }" | ${resource_dir}/in "$4" | tee /dev/stderr
}

put_uri() {
  jq -n "{
    source: {
      uri: $(echo $1 | jq -R .),
      regex: $(echo $2 | jq -R .)
    }
  }" | ${resource_dir}/out "$3" | tee /dev/stderr
}

# run ftp server for testing
init_ftp_server() {
    FTP_ROOT=$1

    local port=$(shuf -i 2000-65000 -n 1)
    vsftpd -olisten_port=${port} -oseccomp_sandbox=NO \
        -oanon_root=${FTP_ROOT} -oanon_upload_enable=YES \
        -owrite_enable=YES \
        -obackground=YES 1>&2

    echo "ftp://localhost:${port}"
}
