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
ORIG="/root/mbtiles/stv.mbtiles"

FULL=$1

PREV_RUN=/data/PREV_RUN
[ ! -f ${PREV_RUN} ] && echo -n 0 > ${PREV_RUN}

CUR=$(date "+%s")
PREV=$(cat $PREV_RUN)

if [[ "$PREV" -eq "$PREV" ]] 2>/dev/null; then
    echo "$(date): Previous run was $((CUR - PREV)) seconds ago"
else
    echo "$(date): Previous run was not detected"
    PREV=0
fi

updates=$(eval sh ${DIR}/selectUpdatedSTVs.sh)

if [[ -f "${ORIG}" && "${FULL}" == "" ]]; then
    if [[ ${#updates[@]} -eq 0 ]]; then
        echo "$(date): Updated STVs: none"
		status=0
    else
        echo "$(date): Updated STVs: ${updates}"
        sh ${DIR}/getSTVGeoJSON.sh $updates
		status=$?
    fi
else
    echo "$(date): Buiding STVs from scratch"
    sh ${DIR}/getSTVGeoJSON.sh
	status=$?
fi

if [ ${status} -eq 0 ]; then
	echo -n ${CUR} > ${PREV_RUN};
	if [ -f /data/stv.mbtiles ]; then
		/bin/mv /data/stv.mbtiles /root/mbtiles/stv.mbtiles;
	fi
fi

exit ${status}
