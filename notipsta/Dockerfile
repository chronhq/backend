FROM morlov/mbtiles-psql:latest

LABEL maintainer="Mikhail Orlov <miklergm@gmail.com>"

COPY notipsta.js /src

ENV NOTIPSTA_PORT=5001
ENV NOTIPSTA_WATCH_INTERVAL=10000

EXPOSE 5001
CMD [ "node", "/src/notipsta.js" ]
