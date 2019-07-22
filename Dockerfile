FROM python:3.6-alpine

LABEL maintainer="whirish <lpoflynn@protonmail.ch>"

ENV PYTHONUNBUFFERED 1

ENV ALPINE_MIRROR "http://dl-cdn.alpinelinux.org/alpine"
RUN echo "${ALPINE_MIRROR}/edge/main" >> /etc/apk/repositories
RUN apk add --update libressl2.7-libcrypto

RUN set -ex \
    && apk --update upgrade \
    && apk add --no-cache alpine-sdk \
    && apk add --no-cache --virtual .build-deps-testing \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    gdal-dev \
    geos-dev \
    proj-dev \
    && apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    musl-dev \
    postgresql-dev \
    linux-headers \
    pcre-dev \
    graphviz

RUN mkdir /config
COPY /config/requirements.txt /config/
RUN pip install -r /config/requirements.txt
COPY /config/firebase.json /config/firebase.json
RUN mkdir /src
WORKDIR /src
EXPOSE 80
CMD ["/bin/ash", "./init.sh", "gunicorn chron.wsgi -b 0.0.0.0:80 -t 300"]
