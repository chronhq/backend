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
from django.db.models import Count
from django.http import Http404, HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import (
    TerritorialEntity,
    PoliticalRelation,
    CachedData,
    City,
    SpacetimeVolume,
    Narrative,
    MapSettings,
    Narration,
    NarrativeVote,
    Profile,
)
from .serializers import (
    TerritorialEntitySerializer,
    PoliticalRelationSerializer,
    CachedDataSerializer,
    CitySerializer,
    SpacetimeVolumeSerializer,
    NarrativeSerializer,
    MapSettingsSerializer,
    NarrationSerializer,
    NarrativeVoteSerializer,
    ProfileSerializer,
)
from .permissions import IsUserOrReadOnly


class TerritorialEntityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TerritorialEntities
    """

    queryset = (
        TerritorialEntity.objects.all().annotate(stv_count=Count("stvs")).order_by("id")
    )
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
        # Dates should be provided in JDN format
        # With values of Jan 01 and Dec 31 for year period
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if wid is not None:
            queryset = queryset.filter(wikidata_id=wid)
        if has_location == "false":
            queryset = queryset.filter(location__isnull=True)
        if start_date is not None and end_date is not None:
            queryset = queryset.filter(date__range=(start_date, end_date))
        return queryset


class CityViewSet(viewsets.ModelViewSet):
    """
    Viewset for Cities
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer


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


class NarrativeVoteViewSet(viewsets.ModelViewSet):
    """
    Viewset for NarrativeVote model
    """

    queryset = NarrativeVote.objects.all()
    serializer_class = NarrativeVoteSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsUserOrReadOnly)

    def create(self, request, *args, **kwargs):
        """
        Deletes instance if vote is null
        """

        request.data["user"] = request.user.id
        if "vote" in request.data and request.data["vote"] is None:
            NarrativeVote.objects.filter(
                narrative=request.data["narrative"], user=request.data["user"]
            ).delete()
            return Response(status.HTTP_204_NO_CONTENT)

        return super().create(request, *args, **kwargs)


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


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Profile
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsUserOrReadOnly)


# https://medium.com/@mrgrantanderson/https-medium-com-serving-vector-tiles-from-django-38c705f677cf
def mvt_cacheddata(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for CachedData.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT ST_AsMVT(tile, 'events') as events
                FROM (
                    SELECT wikidata_id, event_type, rank, year, geom, date::INTEGER
                    FROM (
                        SELECT *, row_number() OVER (PARTITION BY year order by rank desc) as i
                        FROM (
                            SELECT * FROM (
                                SELECT *
                                    , EXTRACT(
                                        year from TO_DATE(TO_CHAR(date, '9999999999.9'), 'J')
                                    ) as year
                                    , ST_AsMVTGeom(
                                        ST_Transform(location, 3857), TileBBox(%s, %s, %s)
                                    ) as geom
                                FROM api_cacheddata
                                ORDER BY rank DESC
                            ) as foo
                            WHERE geom IS NOT NULL
                        ) as foo
                    ) as foo
                    WHERE i <= 20
                ) AS tile
            """,
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
            """
                SELECT ST_AsMVT(tile, 'cities') as cities
                FROM (
                    SELECT id, wikidata_id, label, inception_date, dissolution_date,
                        ST_AsMVTGeom(ST_Transform(location, 3857), TileBBox(%s, %s, %s))
                    FROM api_city
                ) AS tile
            """,
            [zoom, x_cor, y_cor],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            raise Http404()
    return HttpResponse(tile, content_type="application/x-protobuf")


def mvt_narration_events(request, narrative, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for attached_events in a given Narrative.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT ST_AsMVT(tile, 'events')
                FROM (
                    SELECT wikidata_id, rank, event_type,
                        ST_AsMVTGeom(ST_Transform(location, 3857), TileBBox(%s, %s, %s)) as geom
                    FROM (
                        SELECT api_cacheddata.* FROM api_narration
                        JOIN api_narration_attached_events ON
                            (api_narration.id = api_narration_attached_events.narration_id)
                        JOIN api_cacheddata ON
                            (api_narration_attached_events.cacheddata_id = api_cacheddata.id)
                        WHERE narrative_id = %s
                    ) AS foo
                ) AS tile
            """,
            [zoom, x_cor, y_cor, narrative],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            raise Http404()
    return HttpResponse(tile, content_type="application/x-protobuf")


def mvt_stv(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for Political Borders.
    """

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

    with connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT ST_AsMVT(a, 'stv')
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
                                    , %s
                                )
                                , 3857
                            )
                            , 1
                        )
                        , TileBBox(%s, %s, %s)
                    ) as territory
                    , api_spacetimevolume.entity_id
                    , api_territorialentity.wikidata_id
                    , api_territorialentity.color
                    , api_territorialentity.admin_level
                FROM api_spacetimevolume
                JOIN api_territorialentity
                ON api_spacetimevolume.entity_id = api_territorialentity.id
                WHERE territory && TileBBox(%s, %s, %s, 4326)
                ) as a
            """,
            [simplification, zoom, x_cor, y_cor, zoom, x_cor, y_cor],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            raise Http404()
    return HttpResponse(tile, content_type="application/x-protobuf")


def mvt_visual_center(request, zoom, x_cor, y_cor):
    """
    Custom view to serve Mapbox Vector Tiles for Country Labels.
    """

    with connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT ST_AsMVT(a, 'visual_center')
                FROM (
                    SELECT
                    api_spacetimevolume.id
                    , api_spacetimevolume.start_date::INTEGER
                    , api_spacetimevolume.end_date::INTEGER
                    , ST_AsMVTGeom(
                        ST_Transform(
                            api_spacetimevolume.visual_center
                            , 3857
                        )
                        , TileBBox(%s, %s, %s)
                    ) as visual_center
                    , api_territorialentity.label
                    , api_territorialentity.admin_level
                FROM api_spacetimevolume
                JOIN api_territorialentity
                ON api_spacetimevolume.entity_id = api_territorialentity.id
                WHERE visual_center && TileBBox(%s, %s, %s, 4326)
                ) as a
            """,
            [zoom, x_cor, y_cor, zoom, x_cor, y_cor],
        )
        tile = bytes(cursor.fetchone()[0])
        if not tile:
            raise Http404()
    return HttpResponse(tile, content_type="application/x-protobuf")
