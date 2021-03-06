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


def te_list(request):
    # pylint: disable=R5102
    """
    Custom view to serve list of the Territorial Entities faster
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT json_agg(row_to_json(foo))::text FROM (
                SELECT
                    id, wikidata_id, color_id AS color, admin_level,
                    dissolution_date, inception_date, label,
                    (CASE WHEN stvs IS NOT null THEN stvs ELSE '[]'::json END) AS stvs,
                    (
                        CASE WHEN stvs IS NOT null THEN json_array_length(stvs) ELSE 0 END
                    ) AS stv_count
                    FROM (
                    SELECT entity, json_agg(row_to_json(foo)) AS stvs FROM (
                        SELECT
                            entity_id as entity,
                            id,
                            start_date,
                            end_date,
                            ST_AsGeoJSON(visual_center)::json AS visual_center,
                            "references"
                        FROM api_spacetimevolume
                        ) as foo
                    GROUP BY entity
                ) as stvs
                FULL OUTER JOIN api_territorialentity ON api_territorialentity.id = entity
            ) as foo
            """
        )
        data = cursor.fetchone()[0]
        if data is None:
            data = "[]"
        return HttpResponse(data, content_type="application/json")
