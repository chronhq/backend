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
import json
from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from jdcal import jd2gcal
from api.models import SpacetimeVolume, HistoricalSpacetimeVolume


def stv_to_geojson_response(stv):
    """
    Function for serializing stv queryset with one member to geojson.
    """

    geojson = serialize(
        "geojson",
        stv,
        geometry_field="territory",
        fields=(
            "start_date",
            "end_date",
            "entity",
            "references",
            "visual_center",
            "related_events",
        ),
    )

    geojson = json.loads(geojson)

    for features in geojson["features"]:
        if not stv[0].visual_center is None:
            features["properties"]["visual_center"] = {
                "type": "Feature",
                "properties": None,
                "geometry": json.loads(stv[0].visual_center.json),
            }
        features["properties"]["entity"] = {
            "label": stv[0].entity.label,
            "pk": stv[0].entity.pk,
        }

    start_date = jd2gcal(stv[0].start_date, 0)
    start_string = "{}-{}-{}".format(start_date[0], start_date[1], start_date[2])

    end_date = jd2gcal(stv[0].end_date, 0)
    end_string = "{}-{}-{}".format(end_date[0], end_date[1], end_date[2])

    response = JsonResponse(geojson)

    response["Content-Disposition"] = "attachment;filename={}_{}_{}.json;".format(
        stv[0].entity.label, start_string, end_string
    )
    return response


def stv_downloader(request, primary_key):
    """
    Download stvs as geojson.
    """

    stv = SpacetimeVolume.objects.filter(pk=primary_key)
    if len(stv) == 0:
        return HttpResponse(status=404)

    return stv_to_geojson_response(stv)


def historical_stv_downloader(request, primary_key):
    """
    Download historical stvs as geojson.
    """

    history = HistoricalSpacetimeVolume.objects.filter(history_id=primary_key)
    if len(history) == 0:
        return HttpResponse(status=404)

    return stv_to_geojson_response(history)
