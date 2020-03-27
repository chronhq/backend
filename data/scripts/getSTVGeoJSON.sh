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

LOCK="/tmp/.getSTVGeoJSON.lock"

if [ -e ${LOCK} ] && kill -0 $(cat ${LOCK}) 2>/dev/null; then
  echo "Lock file exists... exiting"
  exit 1
fi

trap "rm -f ${LOCK}; exit" INT TERM EXIT
echo $$ > ${LOCK}

psql="psql -d \"host=db user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}\" -t -c"

DIR="$( cd "$( dirname "$0" )" && pwd )"
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
      SELECT * FROM view_stvmap WHERE id = $target
    ) row;
  "
}


SEPARATOR=""

if [[ "$#" -eq 0 ]]; then
  LIST=$(eval $psql "'select id from api_spacetimevolume'")
else
  LIST=$@
fi

# build geojson for STVs
echo '{"type": "FeatureCollection","features": [' >| $FCFILE
for id in $LIST; do
  feature "$id"
  res=$(eval $psql "\"$query\"")
  if [ "$res" != "" ]; then
    echo -n $SEPARATOR >> $FCFILE
    echo $res >> $FCFILE
    SEPARATOR=","
  fi
done
echo ']}' >> $FCFILE
echo "$(date): GeoJSON built successfully"

sh ${DIR}/buildMVT.sh $@

rm -rf ${LOCK}
