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
from json.decoder import JSONDecodeError
from cacheops import cached_as
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal.error import GDALException
from django.utils.datastructures import MultiValueDictKeyError
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets

from api.models import SpacetimeVolume
from api.serializers import SpacetimeVolumeSerializer


def _validate_geometry(request):
    content = request.data["territory"].read().decode("utf-8")
    try:
        try:
            # Parse GeoJSON FeatureCollection
            geom = GEOSGeometry("POINT EMPTY", srid=4326)
            features = json.loads(content)
            for feature in features["features"]:
                feature_geom = feature["geometry"]
                if "crs" in features:  # Copy SRID data if present
                    feature_geom["crs"] = features["crs"]
                geom = geom.union(GEOSGeometry(json.dumps(feature_geom)))
        except (GDALException, KeyError, JSONDecodeError):
            geom = GEOSGeometry(content)
    except GDALException:
        raise ValidationError("Geometry is not recognized")
    if geom.geom_type not in ["Polygon", "MultiPolygon"]:
        raise ValidationError("Invalid geometry type")
    if geom.srid != 4326:
        raise ValidationError("Geometry SRID must be 4326")
    return geom


def _stv_form_validate(request):
    """
    Validate form params
    """
    if not issubclass(type(request.data.get("territory", None)), UploadedFile):
        raise ValidationError("Territory file is missing")

    try:
        start_date = float(request.data["start_date"])
        end_date = float(request.data["end_date"])
        if start_date >= end_date:
            raise ValueError
    except (ValueError, MultiValueDictKeyError):
        raise ValidationError("Use JDN for start_date and end_date")

    geom = _validate_geometry(request)

    try:
        request.data["visual_center"] = GEOSGeometry(request.data["visual_center"])
    except (KeyError, GDALException):
        request.data.pop("visual_center", None)

    return geom, start_date, end_date


def _overlaps_queryset(geom, start_date, end_date):
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
                        %(geom)s::geometry
                    ) as diff
                FROM (
                    SELECT *
                    FROM api_spacetimevolume as stv
                    WHERE stv.end_date >= %(start_date)s::numeric(10,1)
                        AND stv.start_date <= %(end_date)s::numeric(10,1)
                        AND ST_Intersects(
                            territory,
                        %(geom)s::geometry)
                ) as foo
            ) as foo
        ) as foo
        WHERE ST_Dimension(xing) = 2 AND ST_Area(xing) > 10
        GROUP BY id, entity_id, start_date, end_date
        """,
        {"geom": geom.ewkt, "start_date": start_date, "end_date": end_date},
    )


def _subtract_geometry(request, overlaps, geom):
    for entity, stvs in overlaps["db"].items():
        overlaps[
            "keep"
            if entity not in request.data["overlaps"]
            or request.data["overlaps"][entity]
            else "modify"
        ].extend(SpacetimeVolume.objects.get(pk__in=stvs))

    # Important to subtract from staging geometry first
    for overlap in overlaps["keep"]:
        geom = geom.difference(overlap.territory)

    for overlap in overlaps["modify"]:
        overlap.territory = overlap.territory.difference(geom)
        overlap.save()


class SpacetimeVolumeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SpacetimeVolumes
    """

    queryset = (
        SpacetimeVolume.objects.all()
        .select_related("entity")
        .prefetch_related("related_events")
        .defer("visual_center")
    )
    serializer_class = SpacetimeVolumeSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Solve overlaps if included in request body
        """

        # Validate other data before overlaps
        empty_territory_data = request.data.copy()
        empty_territory_data["territory"] = "POINT (0 0)"
        serializer = self.get_serializer(data=empty_territory_data)
        serializer.is_valid(raise_exception=True)

        geom, start_date, end_date = _stv_form_validate(request)

        def _overlaps():
            # Note that we are using list for queryset here,
            # it's because we don't want to cache queryset object but results.
            return list(_overlaps_queryset(geom, start_date, end_date))

        if "cacheops" in settings.INSTALLED_APPS:
            # Cache overlaps query in production
            _overlaps = (
                cached_as(
                    SpacetimeVolume.objects.filter(
                        territory__overlaps=geom,
                        start_date__lte=end_date,
                        end_date__gte=start_date,
                    ),
                    extra=(start_date, end_date),
                )
            )(_overlaps)

        # keep or modify STVs on server
        # "keep|modify": ["stv_id", "stv_id" ...]
        overlaps = {"keep": [], "modify": []}
        # Generate list of overlaps grouped by entities
        # { "entity_id": ["stv_id", "stv_id"], ...}
        overlaps["db"] = {}
        for i in _overlaps():
            if i.entity.pk not in overlaps["db"]:
                overlaps["db"][i.entity.pk] = []
            overlaps["db"][i.entity.pk].append(i.pk)

        if "overlaps" not in request.data and len(overlaps["db"]) > 0:
            return JsonResponse({"overlaps": overlaps["db"]}, status=409)

        _subtract_geometry(request, overlaps, geom)

        request.data["territory"] = geom
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update STVs references, visual_center and entity_id
        """
        stv = SpacetimeVolume.objects.get(pk=kwargs["pk"])
        request.POST._mutable = True  # pylint: disable=W0212
        request.POST.update(
            {
                "territory": stv.territory,
                "start_date": stv.start_date,
                "end_date": stv.end_date,
            }
        )
        try:
            request.POST["visual_center"] = GEOSGeometry(request.data["visual_center"])
        except (KeyError, GDALException):
            request.data.pop("visual_center", None)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, pk):
        try:
            SpacetimeVolume.objects.get(pk=pk).delete()
            return JsonResponse({"status": "ok"}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Does not exist"}, status=410)
