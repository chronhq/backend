FROM python:3-alpine as base

LABEL maintainer="whirish <lpoflynn@protonmail.ch>"

ENV PYTHONUNBUFFERED 1
ENV PYTHONUSERBASE /opt/python
ENV PATH="/opt/python/bin:${PATH}"

ENV ALPINE_MIRROR "http://dl-cdn.alpinelinux.org/alpine"
RUN echo "${ALPINE_MIRROR}/edge/main" >> /etc/apk/repositories

FROM base as deps

RUN set -ex \
    && apk add --no-cache --update libressl2.9-libcrypto \
    && apk add --no-cache alpine-sdk \
    && apk add --no-cache --virtual .build-deps-testing \
    --repository ${ALPINE_MIRROR}/edge/testing \
    gdal-dev \
    geos-dev \
    proj-dev \
    && apk add --no-cache --virtual .build-deps \
    postgresql-dev \
    linux-headers \
    pcre-dev \
    graphviz

COPY /config/requirements.txt /
RUN pip install -r /requirements.txt --user --upgrade

FROM base

RUN apk add --no-cache \
    postgresql binutils
RUN apk add --no-cache --repository ${ALPINE_MIRROR}/edge/testing \
    gdal-dev geos-dev

COPY --from=deps /opt/python /opt/python/
RUN mkdir /{config,src}

COPY /config/firebase.json /config/firebase.json
WORKDIR /src
EXPOSE 80
CMD ["/bin/ash", "./init.sh", "gunicorn chron.wsgi -b 0.0.0.0:80 -t 300"]
