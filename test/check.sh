#!/bin/sh

# test the check command

set -e

source $(dirname $0)/helpers.sh

# should be able to return the version of a file on the ftp server
it_can_check_a_file(){
    # create test ftp root
    FTP_ROOT=$(mktemp -d ${TMPDIR_ROOT}/ftp-root.XXXXXX)
    chmod a+rx ${FTP_ROOT}

    ref=0.0.1
    path=/
    regex="file-(.*).tgz"

    # create test file
    touch ${FTP_ROOT}/file-${ref}.tgz

    # create test ftp server
    local uri=$(init_ftp_server ${FTP_ROOT})

    # run check command
    check_uri $uri/$path $regex | jq -e "
    . == [{ref: $(echo $ref | jq -R .)}]
    "
}

# should be able to return the versions of multiple file on the ftp server
it_can_check_multiple_file(){
    # create test ftp root
    FTP_ROOT=$(mktemp -d ${TMPDIR_ROOT}/ftp-root.XXXXXX)
    chmod a+rx ${FTP_ROOT}

    refs="0.0.2 0.0.1"
    path=/
    regex="file-(.*).tgz"

    # create test file
    for ref in $refs;do
        touch ${FTP_ROOT}/file-${ref}.tgz
    done

    # create test ftp server
    local uri=$(init_ftp_server ${FTP_ROOT})

    # run check command
    check_uri $uri/$path $regex | jq -e '
    . == [{"ref": "0.0.1"}, {"ref": "0.0.2"}]
    '
}

run it_can_check_a_file
run it_can_check_multiple_file
