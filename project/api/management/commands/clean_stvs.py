"""
Chron.
Copyright (C) 2018 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
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

from itertools import tee

from django.db import transaction, connection
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from django.contrib.gis.db.models.functions import MakeValid

from api.models import TerritorialEntity, SpacetimeVolume
from api.views.stv_view import find_difference, calculate_area


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)  # pylint: disable=invalid-name
    next(b, None)
    return zip(a, b)


def make_stvs_valid(entity):
    """ Update STVs with invalid geometry """
    stvs = SpacetimeVolume.objects.filter(entity=entity)
    for stv in stvs:
        if not stv.territory.valid:
            print(
                "- Making STV #{} [{} - {}] valid".format(
                    stv.id, stv.start_date, stv.end_date
                )
            )
            stvs.filter(id=stv.id).update(territory=MakeValid("territory"))


def fix_antimeridian(timestamp=None):
    """ Fix polygons along 180th meridian """
    options = {
        "antimeridian_positive": "SRID=4326;LINESTRING(180 90,180 -90)",
        "antimeridian_negative": "SRID=4326;LINESTRING(-180 90,-180 -90)",
        "timestamp": timestamp,
    }

    initial = (
        "api_spacetimevolume"
        if timestamp is None
        else """
        (SELECT api_spacetimevolume.* FROM (
                SELECT DISTINCT id
                FROM api_historicalspacetimevolume WHERE history_date >= to_timestamp(%(timestamp)s)
            ) AS foo
            JOIN api_spacetimevolume ON foo.id = api_spacetimevolume.id
        ) AS foo
    """
    )

    ids_req = """
        SELECT array_agg(id)
        FROM {}
        WHERE
            ST_Intersects(territory, ST_GeomFromEWKT(%(antimeridian_positive)s))
        OR	ST_Intersects(territory, ST_GeomFromEWKT(%(antimeridian_negative)s))
    """.format(  # nosec
        initial
    )

    with connection.cursor() as cursor:
        cursor.execute(ids_req, options)
        ids = cursor.fetchone()[0]
        if ids is not None:
            options["ids"] = ids
            print(
                "Fixing issues around antimeridian. Total polygons {}".format(len(ids))
            )
            cursor.execute(
                """
                UPDATE api_spacetimevolume
                SET territory=foo.territory
                FROM (
                    SELECT id,
                        ST_Split(ST_Split(
                            territory, ST_GeomFromEWKT(%(antimeridian_positive)s)
                            ), ST_GeomFromEWKT(%(antimeridian_negative)s)
                        ) AS territory
                    FROM (
                        SELECT * FROM api_spacetimevolume WHERE id=ANY(%(ids)s)
                    ) AS foo
                    WHERE ST_IsValid(ST_Transform(territory, 3857)) is not True
                ) AS foo
                WHERE api_spacetimevolume.id = foo.id
                """,
                options,
            )
            affected = cursor.rowcount
            print("{} rows affected".format(affected))


@transaction.atomic
def recreate_stvs(to_create, to_remove):
    """ Update STVs in database """
    SpacetimeVolume.objects.filter(pk__in=to_remove).delete()
    for stv in to_create:
        SpacetimeVolume.objects.create(**stv)


def handle_te_time(entity):
    """ Prepare changes in list of Spacetimve Volumes for provided Territorial Entity """
    stvs = SpacetimeVolume.objects.filter(entity=entity)
    dates = []
    to_remove = []
    to_create = []

    for stv in stvs:
        dates.extend([stv.start_date, stv.end_date + 1])
    dates = sorted(set(dates))

    for start, next_start in pairwise(dates):
        end = next_start - 1
        if int(end - start) <= 1:
            continue

        overlaps = SpacetimeVolume.objects.filter(
            entity=entity, start_date__lte=start, end_date__gte=end
        )
        if overlaps.count() == 1:
            stv = overlaps[0]
            if not (stv.start_date == start and stv.end_date == end):
                print(
                    "[{} - {}]: Using geometry from STV #{} [{} - {}]".format(
                        start, end, stv.id, stv.start_date, stv.end_date
                    )
                )
                to_create.append(
                    {
                        "entity": entity,
                        "start_date": start,
                        "end_date": end,
                        "territory": stv.territory,
                    }
                )
                to_remove.append(stv.id)
        if overlaps.count() > 1:
            print(
                "[{} - {}]: Creating union of {} STVs".format(
                    start, end, overlaps.count()
                )
            )
            geom = GEOSGeometry("POINT EMPTY", srid=4326)
            for stv in overlaps:
                print(
                    "\t...STV #{} [{} - {}]".format(
                        stv.id, stv.start_date, stv.end_date
                    )
                )
                geom = geom.union(stv.territory)
                to_remove.append(stv.id)
            to_create.append(
                {
                    "entity": entity,
                    "start_date": start,
                    "end_date": end,
                    "territory": geom,
                }
            )
    to_remove = sorted(set(to_remove))
    if len(to_create) > 0 or len(to_remove) > 0:
        print("> Unique dates {}".format(len(dates)))
        print("+ Total STVs to create count({})".format(len(to_create)))
        print("- Total STVs to remove count({})".format(len(to_remove)))
        recreate_stvs(to_create, to_remove)


@transaction.atomic
def handle_stv_duplicates(entity):
    """ Join STVs with identical geometry """
    stvs = SpacetimeVolume.objects.filter(entity=entity).order_by("start_date")
    for prev, cur in pairwise(stvs):
        if cur.start_date - prev.end_date > 1:
            continue
        areas = [calculate_area(prev.territory), calculate_area(cur.territory)]
        # Skip big difference
        if abs(areas[0] - areas[1]) > 100:
            continue
        if areas[0] == areas[1]:
            diff = None
        else:
            diff = find_difference(cur.territory, prev.territory)
            if diff is None:
                diff = find_difference(prev.territory, cur.territory)

        if diff is None:
            print(
                "= Combining STV #{} [{} - {}] {} + STV #{} [{} - {}] {}".format(
                    prev.id,
                    prev.start_date,
                    prev.end_date,
                    areas[0],
                    cur.id,
                    cur.start_date,
                    cur.end_date,
                    areas[1],
                )
            )
            cur.start_date = prev.start_date
            prev.delete()
            cur.save()


class Command(BaseCommand):

    """
    Clean time overlaps for STVs
    """

    help = "Clean time overlaps for STVs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--time-overlaps", action="store_true", help="Fix STVs time overlaps"
        )
        parser.add_argument(
            "--duplicates", action="store_true", help="Merge identical STVs"
        )
        parser.add_argument(
            "--make-valid", action="store_true", help="Fix polygons to be valid"
        )
        parser.add_argument(
            "--antimeridian", action="store_true", help="Fix polygons on antimeridian",
        )
        parser.add_argument(
            "--all", action="store_true", help="Use all methods to fix STVs"
        )

    def handle(self, *args, **options):
        options_list = ["time_overlaps", "duplicates", "make_valid", "antimeridian"]
        if options["all"]:
            for opt in options_list:
                options[opt] = True

        entities = TerritorialEntity.objects.all()

        for entity in entities:
            if not (
                options["time_overlaps"]
                or options["duplicates"]
                or options["make_valid"]
            ):
                break
            print(
                "Processing Territorial Entity: {}, id {}".format(
                    entity.label, entity.id
                )
            )
            if SpacetimeVolume.objects.filter(entity=entity).count() == 0:
                print("* Removing empty entity")
                entity.delete()
                continue
            if options["make_valid"]:
                make_stvs_valid(entity)
            if options["time_overlaps"]:
                handle_te_time(entity)
            if options["duplicates"]:
                handle_stv_duplicates(entity)
        if options["antimeridian"]:
            fix_antimeridian()
