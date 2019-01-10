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

from rest_framework.serializers import ModelSerializer, IntegerField

from .models import (
    TerritorialEntity,
    PoliticalRelation,
    CachedData,
    AtomicPolygon,
    SpacetimeVolume,
    Narrative,
    MapSettings,
    Narration,
)


class TerritorialEntitySerializer(ModelSerializer):
    """
    Serializes the TerritorialEntity model
    """

    class Meta:
        model = TerritorialEntity
        fields = "__all__"


class PoliticalRelationSerializer(ModelSerializer):
    """
    Serializes the PoliticalRelation model
    """

    class Meta:
        model = PoliticalRelation
        fields = "__all__"


class CachedDataSerializer(ModelSerializer):
    """
    Serializes the CachedData model
    """

    event_type = IntegerField(min_value=0)

    class Meta:
        model = CachedData
        fields = "__all__"
        read_only_fields = ("rank",)


class AtomicPolygonSerializer(ModelSerializer):
    """
    Serializes the PoliticalRelation model
    """

    class Meta:
        model = AtomicPolygon
        fields = "__all__"


class SpacetimeVolumeSerializer(ModelSerializer):
    """
    Serializes the SpacetimeVolume model
    """

    class Meta:
        model = SpacetimeVolume
        fields = "__all__"


class NarrativeSerializer(ModelSerializer):
    """
    Serializes the Narrative model
    """

    class Meta:
        model = Narrative
        fields = "__all__"


class MapSettingsSerializer(ModelSerializer):
    """
    Serializes the MapSettings model
    """

    class Meta:
        model = MapSettings
        fields = "__all__"


class NarrationSerializer(ModelSerializer):
    """
    Serializes the Narration model
    """

    class Meta:
        model = Narration
        fields = "__all__"
