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

from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import LimitOffsetPagination

from api.models import (
    TerritorialEntity,
    PoliticalRelation,
    CachedData,
    City,
    Narrative,
    MapSettings,
    Narration,
    NarrativeVote,
    Profile,
    Symbol,
    SymbolFeature,
    HistoricalSpacetimeVolume,
)
from api.serializers import (
    TerritorialEntitySerializer,
    PoliticalRelationSerializer,
    CachedDataSerializer,
    CitySerializer,
    NarrativeSerializer,
    MapSettingsSerializer,
    NarrationSerializer,
    NarrativeVoteSerializer,
    ProfileSerializer,
    SymbolSerializer,
    SymbolFeatureSerializer,
    StvHistoryListSerializer,
    StvHistoryRetrieveSerializer,
)
from api.permissions import IsUserOrReadOnly


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


class SymbolFeatureViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SymbolFeatures, filterable by Symbol id
    """

    queryset = SymbolFeature.objects.all()
    serializer_class = SymbolFeatureSerializer

    def get_queryset(self):
        queryset = self.queryset
        symbol = self.request.query_params.get("symbol", None)
        if symbol is not None:
            queryset = queryset.filter(symbol=symbol)
        return queryset


class SymbolViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Symbols
    """

    queryset = Symbol.objects.all()
    serializer_class = SymbolSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Profile
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsUserOrReadOnly)


class HistoryPagination(LimitOffsetPagination):
    page_size = 100
    page_size_query_param = 'limit'
    max_page_size = 1000
class StvHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SpacetimeVolume History
    """
    queryset = HistoricalSpacetimeVolume.objects.all()
    pagination_class = HistoryPagination


    def get_queryset(self):

        queryset = self.queryset

        if self.action == 'list':
            stv = self.request.query_params.get('stv', None)
            
            if stv is not None:
                queryset = queryset.filter(id=stv)

            te = self.request.query_params.get('te', None)

            if te is not None:
                queryset = queryset.filter(entity=te)
        
        return queryset

    def get_serializer_class(self):
            if self.action == 'list':
                return StvHistoryListSerializer
            if self.action == 'retrieve':
                return StvHistoryRetrieveSerializer
