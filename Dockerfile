FROM python:3-alpine

ENV LANG C

# install requirements
RUN apk add --no-cache vsftpd
ADD requirements*.txt setup.cfg ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_dev.txt

# install asserts
ADD assets/ /opt/resource/
ADD test/ /opt/resource-tests/

# test
RUN pylama /opt/resource /opt/resource-tests/
RUN RESOURCE_DEBUG=1 py.test -l --tb=short -r fE /opt/resource-tests

# cleanup test environment
RUN rm -r /tmp/*
RUN pip uninstall -y -r requirements_dev.txt
RUN apk del --no-cache vsftpd
