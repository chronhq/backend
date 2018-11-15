#!/bin/ash

set -e

dbname="postgres"
host="db"
port="5432"
user="postgres"
passwd="postgres"
cmd="$@"

>&2 echo "Waiting for Postgres..."

python wait_for_pg.py $dbname $host $port $user $passwd

>&2 echo "Postgres is up - executing command"

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

exec $cmd
