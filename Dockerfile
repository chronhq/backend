FROM chronmaps/backend:deps-build as build

LABEL maintainer="Mikhail Orlov <miklergm@gmail.com>"

COPY /config/requirements.txt /
RUN pip install -r /requirements.txt --user --upgrade

FROM chronmaps/backend:deps-base as base

COPY --from=build /opt/python /opt/python/

RUN mkdir /config /src

COPY ./project /src
WORKDIR /src
EXPOSE 80
ENTRYPOINT ["/bin/ash", "./init.sh", "gunicorn chron.wsgi -b 0.0.0.0:80 -t 300"]
