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


def mvt_narratives(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for Narratives with Symbols and Attached Events.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT ST_AsMVT(tile, 'narratives') FROM (
                SELECT wikidata_id, rank, event_type, narrative_id,
                    ST_AsMVTGeom(ST_Transform(location, 3857), TileBBox(%s, %s, %s)) as geom
                FROM (
                    SELECT api_cacheddata.*, api_narration.narrative_id FROM api_narration
                    JOIN api_narration_attached_events ON
                        (api_narration.id = api_narration_attached_events.narration_id)
                    JOIN api_cacheddata ON
                        (api_narration_attached_events.cacheddata_id = api_cacheddata.id)
                ) AS foo
            ) AS tile
            --
            UNION
            -- Row 2
            -- Military symbols
            --
            SELECT ST_AsMVT(symbols, 'symbols') FROM (
                SELECT
                    "order", narrative_id,
                    ST_AsMVTGeom(ST_Transform(geom, 3857), TileBBox(%s, %s, %s)) as geom,
                    styling::json,
                    styling->'layer' AS layer
                FROM api_narration
                JOIN api_symbol_narrations ON api_narration.id = api_symbol_narrations.narration_id
                JOIN api_symbol ON api_symbol_narrations.symbol_id = api_symbol.id
                JOIN api_symbolfeature ON api_symbol.id = api_symbolfeature.symbol_id
            ) as symbols
            """,
            [zoom, x_cor, y_cor, zoom, x_cor, y_cor],
        )

        first_row = cursor.fetchone()[0]
        try:
            tile = bytes(first_row) + bytes(cursor.fetchone()[0])
        except TypeError:
            tile = bytes(first_row)

        if not tile:
            return HttpResponse(status=204)
    return HttpResponse(tile, content_type="application/x-protobuf")
