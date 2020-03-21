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

DIR="$( cd "$( dirname "$0" )" && pwd )"
TMP="/tmp/updateTiles";
mkdir -p $TMP
LOCK="${TMP}/.updateTiles.lock"

if [ -e ${LOCK} ] && kill -0 $(cat ${LOCK}) 2>/dev/null; then
  echo "Lock file exists... exiting"
  exit 1
fi

trap "rm -f ${LOCK}; exit" INT TERM EXIT
echo $$ > ${LOCK}

PREV_RUN="${TMP}/PREV_RUN"
[ ! -f ${PREV_RUN} ] && echo -n 0 > ${PREV_RUN}

CUR=$(date "+%s")
PREV=$(cat $PREV_RUN)

# Change dir to project's root
cd "$DIR/../../"

time docker-compose exec web python manage.py generate_mvt --update --timestamp "$PREV"

[ $? -eq 0 ] && echo -n ${CUR} > ${PREV_RUN}
