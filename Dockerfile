FROM python:3.4

MAINTAINER Daniele Venzano <venza@brownhat.org>

RUN mkdir -p /opt/zoe-logger
WORKDIR /opt/zoe-logger

COPY . /opt/zoe-logger
RUN pip install --no-cache-dir -r requirements.txt

VOLUME /etc/zoe/

RUN python3 ./zoe-logger.py --write-config /etc/zoe/zoe-logger.conf

CMD ./zoe-logger.py
