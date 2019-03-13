#!/bin/bash

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

psql='psql -U postgres -t -c'

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
DATA="${DIR}/../data"
mkdir -p $DATA
FCFILE="${DATA}/ap.json"

TABLE='api_atomicpolygon'

echo $DIR

function feature() {
  local target="$1"
  query="
    SELECT jsonb_build_object(
      'type',       'Feature',
      'id',         id,
      'geometry',   ST_AsGeoJSON(geom)::json,
      'properties', to_jsonb(row) - 'geom'
    ) FROM (
      SELECT
        array_agg(foo.spacetimevolume_id) AS stv,
        foo.atomicpolygon_id AS id,
        geom
      FROM (
        SELECT * FROM api_spacetimevolume
        JOIN api_spacetimevolume_territory
          ON api_spacetimevolume_territory.spacetimevolume_id = api_spacetimevolume.id
        ) as foo
        JOIN api_atomicpolygon ON api_atomicpolygon.id = foo.atomicpolygon_id
        WHERE foo.atomicpolygon_id = $target
        GROUP BY foo.atomicpolygon_id, geom
      ) row;
  "
}


SEPARATOR=""

echo '{"type": "FeatureCollection","features": [' > $FCFILE
for id in $($psql "select id from $TABLE"); do
  # echo This is id: $id;
  feature $id
  $psql "$query" >> $FCFILE
  echo -n $SEPARATOR >> $FCFILE
  SEPARATOR=","
done
echo ']}' >> $FCFILE
