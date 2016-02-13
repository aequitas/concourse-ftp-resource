FROM python:3-alpine

ENV LANG C

# test requirements
RUN apk add --no-cache vsftpd jq

ADD requirements.txt requirements.txt
ADD setup.cfg setup.cfg
RUN pip install --no-cache-dir -r requirements.txt

ADD assets/ /opt/resource/
RUN chmod +x /opt/resource/*

ADD test/ /opt/resource-tests/
RUN py.test -x -l --tb=short -r fE /opt/resource-tests
RUN pylama /opt/resource /opt/resource-tests/
RUN /opt/resource-tests/all.sh
