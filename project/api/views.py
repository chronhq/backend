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

from django.db import connection
from django.http import Http404, HttpResponse
from rest_framework import viewsets
from silk.profiling.profiler import silk_profile

from .models import (
    TerritorialEntity,
    PoliticalRelation,
    CachedData,
    City,
    AtomicPolygon,
    SpacetimeVolume,
    Narrative,
    MapSettings,
    Narration,
)
from .serializers import (
    TerritorialEntitySerializer,
    PoliticalRelationSerializer,
    CachedDataSerializer,
    CitySerializer,
    AtomicPolygonSerializer,
    SpacetimeVolumeSerializer,
    NarrativeSerializer,
    MapSettingsSerializer,
    NarrationSerializer,
)


class TerritorialEntityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TerritorialEntities
    """

    queryset = TerritorialEntity.objects.all()
    serializer_class = TerritorialEntitySerializer


class PoliticalRelationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PoliticalRelations
    """

    queryset = PoliticalRelation.objects.all()
    serializer_class = PoliticalRelationSerializer


class CachedDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CachedData
    """

    queryset = CachedData.objects.all().order_by("-rank")
    serializer_class = CachedDataSerializer

    def get_queryset(self):
        queryset = self.queryset
        wid = self.request.query_params.get("wikidata_id", None)
        has_location = self.request.query_params.get("has_location", None)
        year = self.request.query_params.get("year", None)
        if wid is not None:
            queryset = queryset.filter(wikidata_id=wid)
        if has_location == "false":
            queryset = queryset.filter(location__isnull=True)
        if year is not None:
            queryset = queryset.filter(date__year=year)
        return queryset


class CityViewSet(viewsets.ModelViewSet):
    """
    Viewset for Cities
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer


class AtomicPolygonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AtomicPolygons
    """

    queryset = AtomicPolygon.objects.all()
    serializer_class = AtomicPolygonSerializer


class SpacetimeVolumeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SpacetimeVolumes
    """

    queryset = (
        SpacetimeVolume.objects.all()
        .select_related("entity")
        .prefetch_related("related_events", "territory")
    )
    serializer_class = SpacetimeVolumeSerializer

    @silk_profile(name="SpacetimeVolumeViewSet")
    def list(self, request, *args, **kwargs):
        print("*")
        return super(SpacetimeVolumeViewSet, self).list(request, *args, **kwargs)


class NarrativeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Narratives
    """

    queryset = Narrative.objects.all()
    serializer_class = NarrativeSerializer


class MapSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MapSettings
    """

    queryset = MapSettings.objects.all()
    serializer_class = MapSettingsSerializer

    def get_queryset(self):
        queryset = self.queryset
        narrative = self.request.query_params.get("narrative", None)
        if narrative is not None:
            queryset = queryset.filter(narration__narrative=narrative)
        return queryset


class NarrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Narrations
    """

    queryset = Narration.objects.all()
    serializer_class = NarrationSerializer

    def get_queryset(self):
        queryset = self.queryset
        narrative = self.request.query_params.get("narrative", None)
        if narrative is not None:
            queryset = queryset.filter(narrative=narrative)
        return queryset


# https://medium.com/@mrgrantanderson/https-medium-com-serving-vector-tiles-from-django-38c705f677cf
def mvt_cacheddata(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for CachedData.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            (
                " SELECT ST_AsMVT(tile, 'events') as events FROM ("
                " SELECT wikidata_id, event_type, rank, year, geom FROM ("
                " SELECT *, row_number() OVER (PARTITION BY year order by rank desc) as i"
                " FROM ( SELECT * FROM ("
                " SELECT *, EXTRACT(year from date) as year,"
                " ST_AsMVTGeom(ST_Transform(location, 3857), TileBBox(%s, %s, %s)) as geom"
                " FROM api_cacheddata"
                " ORDER BY rank DESC"
                " ) as foo WHERE geom IS NOT NULL ) as foo) as foo"
                " WHERE i <= 20) AS tile"
            ),
            [zoom, x_cor, y_cor],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            raise Http404()
    return HttpResponse(tile, content_type="application/x-protobuf")


def mvt_cities(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for Cities.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            (
                "SELECT ST_AsMVT(tile, 'cities') as cities FROM ("
                "SELECT id, wikidata_id, label,"
                "EXTRACT(year from inception_date) as inception_date,"
                "EXTRACT(year from dissolution_date) as dissolution_date,"
                "ST_AsMVTGeom(ST_Transform(location, 3857), TileBBox(%s, %s, %s)) "
                "FROM api_city) AS tile"
            ),
            [zoom, x_cor, y_cor],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            raise Http404()
    return HttpResponse(tile, content_type="application/x-protobuf")


def mvt_narration_events(request, narration, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for attached_events in a given Narration.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            (
                "SELECT ST_AsMVT(tile, 'narrative') FROM ("
                "SELECT id, wikidata_id, rank, EXTRACT(year from date) as date, "
                "ST_AsMVTGeom(ST_Transform(location, 3857), TileBBox(%s, %s, %s)) "
                "FROM api_cacheddata WHERE id = ("
                "SELECT cacheddata_id FROM api_narration_attached_events "
                "WHERE narration_id = %s)) AS tile"
            ),
            [zoom, x_cor, y_cor, narration],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            raise Http404()
    return HttpResponse(tile, content_type="application/x-protobuf")
