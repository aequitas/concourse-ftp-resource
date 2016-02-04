#!/bin/sh

set -e

source $(dirname $0)/helpers.sh

it_can_put_a_file(){
    # create test ftp root
    FTP_ROOT=$(mktemp -d ${TMPDIR_ROOT}/ftp-root.XXXXXX)
    chmod a+rx ${FTP_ROOT}
    mkdir ${FTP_ROOT}/test
    chmod a+w ${FTP_ROOT}/test

    src_dir=$(mktemp -d ${TMPDIR_ROOT}/ftp-dest.XXXXXX)
    regex="file-(.*).tgz"
    ref=0.0.1
    path=test

    # create test file
    echo $$ > ${src_dir}/file-${ref}.tgz

    # create test ftp server
    local uri=$(init_ftp_server ${FTP_ROOT})

    # run get command
    put_uri $uri/$path $regex $src_dir | jq -e "
    .version == {ref: $(echo file-${ref}.tgz | jq -R .)}
    "

    # test if file exists and has right content
    test -e ${FTP_ROOT}/${path}/file-${ref}.tgz
    diff ${src_dir}/file-${ref}.tgz ${FTP_ROOT}/${path}/file-${ref}.tgz
}

run it_can_put_a_file
