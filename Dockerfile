FROM python:3.6-alpine

LABEL maintainer="whirish <lpoflynn@protonmail.ch>"

ENV PYTHONUNBUFFERED 1

RUN sed -i -e 's/v3\.7/edge/g' /etc/apk/repositories && \
    apk upgrade --update-cache --available

RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev libffi-dev && \
    apk add postgresql-dev && \
    apk add --no-cache --virtual .build-deps-testing \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    gdal-dev \
    geos-dev \
    proj4-dev

RUN mkdir /config
COPY /config/requirements.txt /config/
RUN pip install -r /config/requirements.txt
RUN mkdir /src
WORKDIR /src
EXPOSE 80
CMD ["/bin/ash", "./init.sh", "gunicorn chron.wsgi -b 0.0.0.0:80"]
