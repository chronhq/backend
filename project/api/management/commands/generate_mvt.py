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
from django import db
from django.core.management.base import BaseCommand
from api.models import TileLayout, MVTLayers

from .clean_stvs import fix_antimeridian

try:
    THREADS = os.cpu_count() - 1
except TypeError:
    THREADS = 1
THREADS = int(os.environ.get("MVT_THREADS", THREADS))

ZOOM = int(os.environ.get("ZOOM", 8))


def split_list(alist, wanted_parts=1):
    """ Split array into smaller arrays """
    length = len(alist)
    return [
        alist[i * length // wanted_parts : (i + 1) * length // wanted_parts]
        for i in range(wanted_parts)
    ]


def create_tile_layout(zoom, x_coor, y_coor):
    """ Add one TileLayout entity with plain SQL query """
    with db.connection.cursor() as cursor:
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

    with db.connection.cursor() as cursor:
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
            WHERE ST_Intersects(territory, TileBBox(%(zoom)s, %(x_coor)s, %(y_coor)s, 4326))
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


def mvt_worker(zoom, tiles, total, update, t_id):
    """ Start MVT updating process """
    db.connections.close_all()
    if not update:
        print("Thread #{}, Tiles {}".format(t_id, tiles))
        for y_coor in range(0, total):
            for x_coor in tiles:
                create_mvt_stv(zoom, x_coor, y_coor)
    else:
        print("Thread #{} Updating {} tiles".format(t_id, len(tiles)))
        for tile in tiles:
            create_mvt_stv(tile.zoom, tile.x_coor, tile.y_coor)
    os._exit(0)  # pylint: disable=protected-access


def populate_mvt_stv_layer(zoom, tile_set, update=False):
    """ Populate MVTLayer table with STV """
    tiles = (
        split_list(tile_set, THREADS)
        if update
        else split_list(range(0, tile_set), THREADS)
    )
    pids = []
    db.connections.close_all()
    for t_id in range(0, THREADS):
        newpid = os.fork()
        if newpid == 0:
            mvt_worker(zoom, tiles[t_id], tile_set, update, t_id)
        else:
            pids.append(newpid)
    for pid in pids:
        os.waitpid(pid, 0)


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
    print("Total tiles to update", len(tiles))
    populate_mvt_stv_layer(0, tiles, True)


class Command(BaseCommand):
    """ Populate database with MVT for STVs """

    def add_arguments(self, parser):
        parser.add_argument(
            "--update", action="store_true", help="Update STVs",
        )
        parser.add_argument("--timestamp", type=int, help="Previous run", default=0)

    def handle(self, *args, **options):
        # Remove tiles with precision greater than zoom
        TileLayout.objects.filter(zoom__gt=ZOOM).delete()
        MVTLayers.objects.filter(zoom__gt=ZOOM).delete()

        for zoom in range(0, ZOOM + 1):
            tiles = pow(2, zoom)
            new_layout = populate_tile_layout(zoom, tiles)
            if not options["update"] or new_layout:
                print(
                    "Generating tiles for zoom {}. Tiles per row {}".format(zoom, tiles)
                )
                populate_mvt_stv_layer(zoom, tiles)
        if options["update"] and not new_layout:
            fix_antimeridian(options["timestamp"])
            update_affected_mvts(options["timestamp"])
