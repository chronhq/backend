#!/bin/ash

set -e

dbname=$POSTGRES_DB
host="db"
port="5432"
user=$POSTGRES_USER
passwd=$POSTGRES_PASSWORD

. /opt/pysetup/.venv/bin/activate

>&2 echo "Waiting for Postgres..."

python wait_for_pg.py $dbname $host $port $user $passwd

>&2 echo "Postgres is up - executing command"

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"
