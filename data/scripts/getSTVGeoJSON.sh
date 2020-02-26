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

psql="psql -d \"host=db user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}\" -t -c"

DATA="/data"
mkdir -p $DATA
LAYER='stv'
FCFILE="${DATA}/${LAYER}.json"


function feature() {
  local target="$1"
  query="
    SELECT jsonb_build_object(
      'type',       'Feature',
      'id',         id,
      'geometry',   ST_AsGeoJSON(territory)::json,
      'properties', to_jsonb(row) - 'territory'
    ) FROM (
      SELECT
        api_spacetimevolume.id,
        api_spacetimevolume.start_date,
        api_spacetimevolume.end_date,
        api_spacetimevolume.references,
        ST_AsGeoJSON(api_spacetimevolume.visual_center)::json as visual_center,
        api_spacetimevolume.territory,
        api_spacetimevolume.entity_id,
        api_territorialentity.wikidata_id, api_territorialentity.color,
        api_territorialentity.admin_level
        FROM api_spacetimevolume
        JOIN api_territorialentity ON api_spacetimevolume.entity_id = api_territorialentity.id
        WHERE api_spacetimevolume.id = $target
      ) row;
  "
}


SEPARATOR=""

if [[ "$#" -eq 0 ]]; then
  # build geojson for all STVs
  echo '{"type": "FeatureCollection","features": [' > $FCFILE
  for id in $(eval $psql "'select id from $TABLE'"); do
    # echo This is id: $id;
    echo -n $SEPARATOR >> $FCFILE
    feature "$id"
    eval $psql "\"$query\"" >> $FCFILE
    SEPARATOR=","
  done
  echo ']}' >> $FCFILE
  echo "GeoJSON built successfully"
  sh ./buildMVT.sh
else
  # build geojson for pk=$@
  echo '{"type": "FeatureCollection","features": [' > $FCFILE
  for arg; do
    echo -n $SEPARATOR >> $FCFILE
    feature "$arg"
    eval $psql "\"$query\"" >> $FCFILE
    SEPARATOR=","
  done
  echo ']}' >> $FCFILE
  echo "GeoJSON built successfully"
  sh ./buildMVT.sh $@
fi
