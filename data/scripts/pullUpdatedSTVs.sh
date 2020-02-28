#!/bin/sh

# Chron.
# Copyright (C) 2019 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
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

date=$(date +%D)
time=$(date +%T)
dt="$date $time"

psql="psql -d \"host=db user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}\" -t -c"

query="
SELECT string_agg(DISTINCT id::text, ' ')
FROM api_historicalspacetimevolume
WHERE history_date >= ('${dt}'::date - interval '1 hour')
"

updates=$(eval $psql "\"$query\"")
echo "Updated STVs: ${updates}"
sh ./getSTVGeoJSON.sh $updates
