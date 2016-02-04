#!/bin/sh

# test the check command

set -e

source $(dirname $0)/helpers.sh

# should be able to get a file from the ftp server
it_can_get_a_file(){
    # create test ftp root
    FTP_ROOT=$(mktemp -d ${TMPDIR_ROOT}/ftp-root.XXXXXX)
    chmod a+rx ${FTP_ROOT}

    dest_dir=$(mktemp -d ${TMPDIR_ROOT}/ftp-dest.XXXXXX)
    template='file-{version}.tgz'
    ref=0.0.1
    path=/

    # create test file
    echo $$ > ${FTP_ROOT}/file-${ref}.tgz

    # create test ftp server
    local uri=$(init_ftp_server ${FTP_ROOT})

    # run get command
    get_uri $uri/$path $template $ref $dest_dir | jq -e "
    .version == {ref: $(echo $ref | jq -R .)}
    "

    # test if file exists and has right content
    test -e $dest_dir/file-${ref}.tgz
    diff ${FTP_ROOT}/file-${ref}.tgz $dest_dir/file-${ref}.tgz
}

run it_can_get_a_file
