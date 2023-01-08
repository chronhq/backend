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

from django.contrib.gis.geos import GEOSGeometry
from django.db import connection

AREA_TOLERANCE = 20.0


def find_difference(geom_a, geom_b):
    """
    Calculate difference between two polygons
    None if no difference
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT ST_Union(geom) as geom FROM (
                SELECT (ST_Dump(ST_Difference(p1, p2))).geom FROM (
                    SELECT
                        ST_MakeValid(%(geom_a)s::geometry) as p1,
                        ST_MakeValid(%(geom_b)s::geometry) as p2
                    ) as foo
                ) as foo
                WHERE ST_Dimension(geom) = 2 AND ST_Area(geom::geography) > %(tolerance)s
            """,
            {"geom_a": geom_a.ewkt, "geom_b": geom_b.ewkt, "tolerance": AREA_TOLERANCE},
        )
        row = cursor.fetchone()[0]
    return row


def geom_difference(geom_a, geom_b):
    """ Return a GEOS object from SQL query """
    diff = find_difference(geom_a, geom_b)
    if diff is None:
        return GEOSGeometry("MULTIPOLYGON EMPTY", srid=4326)
    # Might raise GDALException
    return GEOSGeometry(diff)


def calculate_area(geom):
    """
    Calculates area of the provided geometry using geography
    Result would be in square meters
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ST_Area(%(geom)s::geography) AS area", {"geom": geom.ewkt}
        )
        row = cursor.fetchone()[0]
    return row
