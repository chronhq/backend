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
    """
    Custom view to serve list of the Territorial Entities faster
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT json_agg(foo) FROM (
                SELECT
                    api_territorialentity.*,
                    stvs,
                    json_array_length(stvs) AS stv_count
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
                JOIN api_territorialentity ON api_territorialentity.id = entity
            ) as foo
            """
        )
        data = cursor.fetchone()[0]
        if data is None:
            data = '[]'
        return HttpResponse(data, content_type="application/json")
