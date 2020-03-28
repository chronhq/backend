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

MVT_STV_QUERY = """
    SELECT
        id, start_date, end_date, "references", entity_id, wikidata_id, color, admin_level
        , ST_AsMVTGeom(
            ST_SnapToGrid(ST_Transform(ST_Simplify(territory, %(simplification)s), 3857), 1)
            , TileBBox(%(zoom)s, %(x_coor)s, %(y_coor)s)) as territory
    FROM view_stvmap
    WHERE ST_Intersects(territory, TileBBox(%(zoom)s, %(x_coor)s, %(y_coor)s, 4326))
"""


def mvt_geom_simplification(zoom):
    """ Simplification for territory field """
    # For WebMercator (3857) X coordinate bounds are ±20037508.3427892 meters
    # For SRID 4326 X coordinated bounds are ±180 degrees
    # resolution = (xmax - xmin) or (xmax * 2)
    # It is 5-10 times faster work with SRID 4326,
    # We will apply ST_Simplify before ST_Transform
    resolution = 360
    # https://postgis.net/docs/ST_AsMVT.html
    # tile extent in screen space as defined by the specification
    extent = 4096

    # Find safe tolerance for ST_Simplfy
    tolerance = (float(resolution) / 2 ** zoom) / float(extent)
    # Apply additional simplification for distant zoom levels
    tolerance_multiplier = 1 if zoom > 5 else 2.2 - 0.2 * zoom
    simplification = tolerance * tolerance_multiplier
    return simplification


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
        where.append("entity_id=ANY(%(tes)s)")
    if len(stv) > 0:
        where.append("id=ANY(%(stv)s)")

    tile = None
    if len(where) > 0:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ST_AsMVT(a, 'stv_admin') AS tile
                FROM ({} AND ({})) AS a
                """.format(  # nosec
                    MVT_STV_QUERY, " OR ".join(where)
                ),
                {
                    "zoom": zoom,
                    "x_coor": x_coor,
                    "y_coor": y_coor,
                    "simplification": mvt_geom_simplification(zoom),
                    "stv": stv,
                    "tes": tes,
                },
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
