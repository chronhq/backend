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


def mvt_cities(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for Cities.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT ST_AsMVT(tile, 'cities') as cities
            FROM (
                SELECT id, wikidata_id, label, inception_date, dissolution_date,
                    ST_AsMVTGeom(ST_Transform(location, 3857), TileBBox(%s, %s, %s))
                FROM api_city
            ) AS tile
            --
            UNION
            -- Row 2
            -- Visual Center
            --
            SELECT ST_AsMVT(vc, 'visual_center')
                FROM (
                    SELECT
                    api_spacetimevolume.id
                    , api_spacetimevolume.start_date::INTEGER
                    , api_spacetimevolume.end_date::INTEGER
                    , ST_AsMVTGeom(
                        ST_Transform(
                            api_spacetimevolume.visual_center
                            , 3857
                        )
                        , TileBBox(%s, %s, %s)
                    ) as visual_center
                    , api_territorialentity.label
                    , api_territorialentity.admin_level
                FROM api_spacetimevolume
                JOIN api_territorialentity
                ON api_spacetimevolume.entity_id = api_territorialentity.id
                WHERE visual_center && TileBBox(%s, %s, %s, 4326)
                ) as vc
            """,
            [zoom, x_cor, y_cor, zoom, x_cor, y_cor, zoom, x_cor, y_cor],
        )

        first_row = cursor.fetchone()[0]
        try:
            tile = bytes(first_row) + bytes(cursor.fetchone()[0])
        except TypeError:
            tile = bytes(first_row)

        if not tile:
            return HttpResponse(status=204)
    return HttpResponse(tile, content_type="application/x-protobuf")
