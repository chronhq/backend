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

from django.db import connection
from django.http import HttpResponse


def mvt_stv(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for Political Borders.
    """

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

    with connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT ST_AsMVT(a, 'stv')
                FROM (
                SELECT
                    api_spacetimevolume.id
                    , api_spacetimevolume.start_date::INTEGER
                    , api_spacetimevolume.end_date::INTEGER
                    , api_spacetimevolume.references
                    , ST_AsMVTGeom(
                        ST_SnapToGrid(
                            ST_Transform(
                                ST_Simplify(
                                    api_spacetimevolume.territory
                                    , %s
                                )
                                , 3857
                            )
                            , 1
                        )
                        , TileBBox(%s, %s, %s)
                    ) as territory
                    , api_spacetimevolume.entity_id
                    , api_territorialentity.wikidata_id
                    , api_territorialentity.color
                    , api_territorialentity.admin_level
                FROM api_spacetimevolume
                JOIN api_territorialentity
                ON api_spacetimevolume.entity_id = api_territorialentity.id
                WHERE territory && TileBBox(%s, %s, %s, 4326)
                ) as a
            """,
            [simplification, zoom, x_cor, y_cor, zoom, x_cor, y_cor],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            return HttpResponse(status=204)
    return HttpResponse(tile, content_type="application/x-protobuf")
