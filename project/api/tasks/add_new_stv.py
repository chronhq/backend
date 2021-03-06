""" Async STV creation """
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from cacheops import cached_as
from django.conf import settings
from django.db import transaction
from django.contrib.gis.geos import GEOSGeometry

from api.models import TerritorialEntity, SpacetimeVolume
from api.serializers import SpacetimeVolumeSerializer
from api.helpers.overlaps import subtract_geometry, overlaps_queryset


@shared_task
@transaction.atomic
def add_new_stv(geom, overlaps_are_missing, **data):
    """
    Solve overlaps if included in request body
    """
    geom = GEOSGeometry(geom)

    def _overlaps():
        # Note that we are using list for queryset here,
        # it's because we don't want to cache queryset object but results.
        return list(overlaps_queryset(geom, data["start_date"], data["end_date"]))

    if "cacheops" in settings.INSTALLED_APPS:
        # Cache overlaps query in production
        _overlaps = (
            cached_as(
                SpacetimeVolume.objects.filter(
                    territory__overlaps=geom,
                    start_date__lte=data["end_date"],
                    end_date__gte=data["start_date"],
                ),
                extra=(data["start_date"], data["end_date"]),
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

    if overlaps_are_missing and len(overlaps["db"]) > 0:
        return {"response": {"overlaps": overlaps["db"]}, "status": 409}
    data["territory"] = subtract_geometry(data["overlaps"], overlaps, geom)

    data["entity"] = TerritorialEntity.objects.get(id=data["entity"])

    # remove overlaps from data
    data.pop("overlaps", None)
    stv = SpacetimeVolume.objects.create(**data)

    # objects.get() will return entity with computed visual_center
    response = SpacetimeVolumeSerializer(SpacetimeVolume.objects.get(pk=stv.id)).data
    return {"response": response, "status": 201}
