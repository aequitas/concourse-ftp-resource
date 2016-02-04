FROM gliderlabs/alpine:3.3

ENV LANG C

RUN apk add --no-cache python py-pip vsftpd jq
RUN pip install ftputil

ADD assets/ /opt/resource/
RUN chmod +x /opt/resource/*

ADD test/ /opt/resource-tests/
RUN /opt/resource-tests/all.sh && \
  rm -rf /tmp/*
