#!/bin/sh

# fail if one command fails
set -e

# install requirements
apk add --no-cache vsftpd
pip install --no-cache-dir -r requirements_dev.txt

# test
pylama /opt/resource /opt/resource-tests/
py.test -l --tb=short -r fE /opt/resource-tests

# cleanup
rm -r /tmp/*
pip uninstall -y -r requirements_dev.txt
apk del --no-cache vsftpd
