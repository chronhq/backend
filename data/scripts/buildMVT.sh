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

LAYER="stv"

mkdir -p /tmp

ORIG="/root/mbtiles/stv.mbtiles"

IN="/data/${LAYER}.json"
TMP="/tmp/${LAYER}"
OUT="${TMP}.mbtiles"
CLEAN="${TMP}-CLEAN.mbtiles"
UPDATES="${TMP}-UPDATES.mbtiles"


# ash-compatible array join implementation
REMOVE_STRING=""
DELIM=""
for r in $@ ; do
  REMOVE_STRING="${REMOVE_STRING}${DELIM}${r}"
  DELIM=","
done

if [[ "$#" -eq 0 ]]; then
  tippecanoe -o $TMP -f -z${ZOOM} -s EPSG:4326 $IN
else
  tippecanoe -f -o ${UPDATES} -z${ZOOM} -s EPSG:4326 $IN
  tile-join -j '{"*":["!in","id",'"${REMOVE_STRING}"']}' -f -o ${CLEAN} ${ORIG}
  tile-join -f -o ${OUT} ${CLEAN} ${UPDATES}
  rm -f $UPDATES $CLEAN
fi

echo "$(date): Finished building mbtiles"

# Can't be done from here because of the filesystem lock issues
# /bin/mv $TMP $MVT
