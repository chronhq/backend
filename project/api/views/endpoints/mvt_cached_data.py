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

# https://medium.com/@mrgrantanderson/https-medium-com-serving-vector-tiles-from-django-38c705f677cf
def mvt_cacheddata(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for CachedData.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT ST_AsMVT(tile, 'events') as events
                FROM (
                    SELECT wikidata_id, event_type, rank, year, geom, date::INTEGER
                    FROM (
                        SELECT *, row_number() OVER (PARTITION BY year order by rank desc) as i
                        FROM (
                            SELECT * FROM (
                                SELECT *
                                    , EXTRACT(
                                        year from TO_DATE(TO_CHAR(date, '9999999999.9'), 'J')
                                    ) as year
                                    , ST_AsMVTGeom(
                                        ST_Transform(location, 3857), TileBBox(%s, %s, %s)
                                    ) as geom
                                FROM api_cacheddata
                                ORDER BY rank DESC
                            ) as foo
                            WHERE geom IS NOT NULL
                        ) as foo
                    ) as foo
                    WHERE i <= 20
                ) AS tile
            """,
            [zoom, x_cor, y_cor],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            return HttpResponse(status=204)
    return HttpResponse(tile, content_type="application/x-protobuf")
