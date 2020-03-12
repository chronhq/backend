"""
Chron.
Copyright (C) 2020 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
Daniil Mordasov, Liam O'Flynn, Mikhail Orlov.

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
import os
from django.db import connection
from django.core.management.base import BaseCommand
from api.models import TileLayout, MVTLayers

ZOOM = os.environ.get("ZOOM", 4)


def create_tile_layout(zoom, x_coor, y_coor):
    """ Add one TileLayout entity with plain SQL query """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO api_tilelayout (zoom, x_coor, y_coor, bbox)
            SELECT *, TileBBOX(zoom, x_coor, y_coor, 4326) AS bbox
            FROM ( SELECT %s AS zoom, %s AS x_coor, %s AS y_coor ) AS f
            """,
            [zoom, x_coor, y_coor],
        )


def populate_tile_layout(zoom, tiles):
    """ Populate TileLayout table """
    if len(TileLayout.objects.filter(zoom=zoom)) != 0:
        return False
    for y_coor in range(0, tiles):
        for x_coor in range(0, tiles):
            create_tile_layout(zoom, x_coor, y_coor)
    return True


def create_mvt_stv(zoom, x_coor, y_coor):
    """ Mapbox Vector Tiles for Political Borders """
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
            INSERT INTO api_mvtlayers (zoom, x_coor, y_coor, layer, tile)
            SELECT
                %(zoom)s AS zoom
                , %(x_coor)s AS x_coor
                , %(y_coor)s AS y_coor
                , 'stv' AS layer
                , ST_AsMVT(a, 'stv') AS tile
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
                                , %(simplification)s
                            )
                            , 3857
                        )
                        , 1
                    )
                    , TileBBox(%(zoom)s, %(x_coor)s, %(y_coor)s)
                ) as territory
                , api_spacetimevolume.entity_id
                , api_territorialentity.wikidata_id
                , api_territorialentity.color
                , api_territorialentity.admin_level
            FROM api_spacetimevolume
            JOIN api_territorialentity
            ON api_spacetimevolume.entity_id = api_territorialentity.id
            WHERE territory && TileBBox(%(zoom)s, %(x_coor)s, %(y_coor)s, 4326)
            ) as a
            ON CONFLICT (zoom, x_coor, y_coor, layer) DO UPDATE SET tile = EXCLUDED.tile
            """,
            {
                "simplification": simplification,
                "zoom": zoom,
                "x_coor": x_coor,
                "y_coor": y_coor,
            },
        )


def populate_mvt_stv_layer(zoom, tiles):
    """ Populate MVTLayer table with STV """
    print("Generating tiles for zoom {}".format(zoom))
    for y_coor in range(0, tiles):
        for x_coor in range(0, tiles):
            create_mvt_stv(zoom, x_coor, y_coor)


def update_affected_mvts(timestamp):
    """ Update tiles based on history """
    tiles = TileLayout.objects.raw(
        """
        SELECT
            DISTINCT api_tilelayout.id, zoom, x_coor, y_coor
        FROM api_tilelayout
        CROSS JOIN api_historicalspacetimevolume AS hstv
        WHERE
            hstv.history_date > to_timestamp(%s)
            AND ST_Intersects(api_tilelayout.bbox, hstv.territory)
            ORDER BY zoom ASC;
        """,
        [timestamp],
    )
    print("Updating {} tiles".format(len(tiles)))
    for tile in tiles:
        create_mvt_stv(tile.zoom, tile.x_coor, tile.y_coor)


class Command(BaseCommand):
    """ Populate database with MVT for STVs """

    def add_arguments(self, parser):
        parser.add_argument(
            "--update", action="store_true", help="Update STVs",
        )

    def handle(self, *args, **options):
        # Remove tiles with precision greater than zoom
        TileLayout.objects.filter(zoom__gt=ZOOM).delete()
        MVTLayers.objects.filter(zoom__gt=ZOOM).delete()
        for zoom in range(0, ZOOM):
            tiles = pow(2, zoom)
            new_layout = populate_tile_layout(zoom, tiles)
            if not options["update"] or new_layout:
                populate_mvt_stv_layer(zoom, tiles)
        if options["update"] and not new_layout:
            # TODO pass valid timestamp
            update_affected_mvts(0)
