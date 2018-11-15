#!/bin/ash

# Chron.
# Copyright (C) 2018 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
# Daniil Mordasov, Liam O’Flynn, Mikhail Orlov.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
