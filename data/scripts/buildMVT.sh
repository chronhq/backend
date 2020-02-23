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

LAYER="stv"
REMOVE=$1

mkdir -p /tmp

IN="/data/${LAYER}.json"
TMP="/tmp/${LAYER}"

if [[ -z "$1" ]]; then
  tippecanoe -o $TMP -f -z${ZOOM} -s EPSG:4326 $IN
else
  tippecanoe -f -o "$TMP-$REMOVE.mbtiles" -z${ZOOM} -s EPSG:4326 "/data/${LAYER}-${REMOVE}.json"
  tile-join -j '{"*":["!=","id",'"${REMOVE}"']}' -f -o "${TMP}-cleaned.mbtiles" /root/mbtiles/stv.mbtiles
  tile-join -f -o "${TMP}.mbtiles" "${TMP}-cleaned.mbtiles" "$TMP-$REMOVE.mbtiles"
fi

# Can't be done from here because of the filesystem lock issues
# /bin/mv $TMP $MVT
