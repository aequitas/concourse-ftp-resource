FROM python:3-alpine

ENV LANG C

# test requirements
RUN apk add --no-cache vsftpd jq

ADD requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ADD assets/ /opt/resource/
RUN chmod +x /opt/resource/*

ADD test/ /opt/resource-tests/
RUN /opt/resource-tests/all.sh && \
  rm -rf /tmp/*
