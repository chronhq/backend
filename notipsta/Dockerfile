FROM morlov/mbtiles-psql:latest

LABEL maintainer="Mikhail Orlov <miklergm@gmail.com>"

COPY notipsta.js /src

ENV NOTIPSTA_PORT=5000
ENV NOTIPSTA_WATCH_INTERVAL=10000

EXPOSE 5000
CMD [ "node", "/src/notipsta.js" ]
