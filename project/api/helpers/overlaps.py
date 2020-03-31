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

from api.models import SpacetimeVolume

from .geometry import geom_difference, calculate_area, AREA_TOLERANCE


def overlaps_queryset(geom, start_date, end_date):
    """
    Return overlapping STVs
    """
    return SpacetimeVolume.objects.raw(
        """
        SELECT id, entity_id, end_date, start_date, ST_Union(xing) FROM (
            SELECT *,
                (ST_Dump(ST_Intersection(territory, diff))).geom as xing
            FROM (
                SELECT *,
                    ST_Difference(
                        territory,
                        ST_MakeValid(%(geom)s::geometry)
                    ) as diff
                FROM (
                    SELECT *
                    FROM api_spacetimevolume as stv
                    WHERE stv.end_date >= %(start_date)s::numeric(10,1)
                        AND stv.start_date <= %(end_date)s::numeric(10,1)
                        AND ST_Intersects(
                            territory,
                        ST_MakeValid(%(geom)s::geometry))
                ) as foo
            ) as foo
        ) as foo
        WHERE ST_Dimension(xing) = 2 AND ST_Area(xing::geography) > %(tolerance)s
        GROUP BY id, entity_id, start_date, end_date
        """,
        {
            "geom": geom.ewkt,
            "start_date": start_date,
            "end_date": end_date,
            "tolerance": AREA_TOLERANCE,
        },
    )


def subtract_geometry(req_overlaps, overlaps, geom):
    """ Perform actions on db """
    for entity, stvs in overlaps["db"].items():
        overlaps["keep" if str(entity) not in req_overlaps else "modify"].extend(
            SpacetimeVolume.objects.filter(pk__in=stvs)
        )

    # Important to subtract from staging geometry first
    for overlap in overlaps["keep"]:
        geom = geom_difference(geom, overlap.territory)

    if calculate_area(geom) < AREA_TOLERANCE:
        raise ValidationError("Polygon is too small")

    for overlap in overlaps["modify"]:
        overlap.territory = geom_difference(overlap.territory, geom)
        if calculate_area(overlap.territory) < AREA_TOLERANCE:
            overlap.delete()
        else:
            overlap.save()
    return geom
