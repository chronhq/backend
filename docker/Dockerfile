FROM chronmaps/backend:deps-python as python

RUN mkdir /config /src

COPY ./project /src
WORKDIR /src
EXPOSE 80

COPY ./docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD ["gunicorn chron.wsgi -b 0.0.0.0:80 -t 300"]
