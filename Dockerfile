FROM chronmaps/backend:deps-python as python

LABEL maintainer="Mikhail Orlov <miklergm@gmail.com>"

RUN mkdir /config /src

COPY ./project /src
WORKDIR /src
EXPOSE 80
ENTRYPOINT ["/bin/ash", "./init.sh", "gunicorn chron.wsgi -b 0.0.0.0:80 -t 300"]
