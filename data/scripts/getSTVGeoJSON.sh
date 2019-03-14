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
MVT="${DIR}/../mbtiles"
mkdir -p $DATA
LAYER='stv'
FCFILE="${DATA}/${LAYER}.json"
MVTFILE="${MVT}/${LAYER}.mbtiles"

TABLE='api_spacetimevolume'

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
        api_spacetimevolume.id,
        api_spacetimevolume.start_date,
        api_spacetimevolume.end_date,
        api_spacetimevolume.references,
        api_spacetimevolume.visual_center,
        EXTRACT(year from api_spacetimevolume.start_date) as start,
        EXTRACT(year from api_spacetimevolume.end_date) as end,
        geom.geom,
        api_territorialentity.wikidata_id, api_territorialentity.color,
        api_territorialentity.admin_level
        FROM api_spacetimevolume
        JOIN (
            SELECT ST_COLLECT(geom) AS geom, spacetimevolume_id as id FROM api_spacetimevolume_territory
            JOIN api_atomicpolygon ON atomicpolygon_id = api_atomicpolygon.id
            GROUP BY (spacetimevolume_id)
        ) as geom ON geom.id = api_spacetimevolume.id
        JOIN api_territorialentity ON api_spacetimevolume.entity_id = api_territorialentity.id
        WHERE api_spacetimevolume.id = $target
      ) row;
  "
}


SEPARATOR=""

echo '{"type": "FeatureCollection","features": [' > $FCFILE
for id in $($psql "select id from $TABLE"); do
  # echo This is id: $id;
  echo -n $SEPARATOR >> $FCFILE
  feature $id
  $psql "$query" >> $FCFILE
  SEPARATOR=","
done
echo ']}' >> $FCFILE

echo 'To build MVT execute'
echo "tippecanoe -o ${CACHE}/${LAYER}.mbtiles -f -z10 -s EPSG:4326 ${DATA}/${LAYER}.json"
