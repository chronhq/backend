# pylint: disable=C0302

"""
Chron.
Copyright (C) 2020 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
Daniil Mordasov, Liam O’Flynn, Mikhail Orlov.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from django.http import HttpResponse
from django.db import connection
from api.models import MVTLayers
from api.management.commands.generate_mvt import stv_mvt_geom_query


def parse_ints(arr):
    """ keep only integers in array """
    res = []
    for i in arr:
        try:
            clean = int(i)
            res.append(clean)
        except ValueError:
            pass
    return res


def mvt_stv(request, zoom, x_coor, y_coor):
    """
    Custom view to serve Mapbox Vector Tiles for Political Borders.
    """
    tes = parse_ints(request.GET.getlist("te"))
    stv = parse_ints(request.GET.getlist("stv"))

    where = []
    if len(tes) > 0:
        where.append("entity_id IN ({})".format(str(tes)[1:-1]))
    if len(stv) > 0:
        where.append("id IN ({})".format(str(stv)[1:-1]))

    tile = None
    if len(where) > 0:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ST_AsMVT(a, 'stv_admin') AS tile
                FROM ({} AND ({})) AS a
                """.format(stv_mvt_geom_query(zoom), " OR ".join(where)),
                {"zoom": zoom, "x_coor": x_coor, "y_coor": y_coor,},
            )
            tile = bytes(cursor.fetchone()[0])
    else:
        tiles = MVTLayers.objects.filter(
            layer="stv", zoom=zoom, x_coor=x_coor, y_coor=y_coor
        )
        if len(tiles) != 0:
            tile = bytes(tiles[0].tile)

    if tile is not None:
        return HttpResponse(tile, content_type="application/x-protobuf")
    return HttpResponse(status=204)
