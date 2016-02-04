#!/bin/sh

# run test for all three commands and print success when no failure

set -e

export TMPDIR_ROOT=$(mktemp -d /tmp/ftp-tests.XXXXXX)

$(dirname $0)/check.sh
$(dirname $0)/get.sh
$(dirname $0)/put.sh

echo -e '\e[32mall tests passed!\e[0m'

rm -rf $TMPDIR_ROOT
