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

from django.db.models import Count, Case, When
from jdcal import jd2gcal
from rest_framework.serializers import (
    ModelSerializer,
    IntegerField,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)

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


class NarrativeVoteSerializer(ModelSerializer):
    """
    Serializes User votes for Narratives
    """

    def create(self, validated_data):
        """
        Updates NarrativeVote instance if it already exists
        """

        narrative_vote, _ = NarrativeVote.objects.update_or_create(
            narrative=validated_data.get("narrative", None),
            user=validated_data.get("user", None),
            defaults={"vote": validated_data.get("vote", None)},
        )
        return narrative_vote

    class Meta:
        model = NarrativeVote
        validators = []
        fields = "__all__"


class ProfileSerializer(ModelSerializer):
    """
    Serializes the Profile model
    """

    class Meta:
        model = Profile
        fields = "__all__"


class SpacetimeVolumeSerializerNoTerritory(ModelSerializer):
    """
    Serializes the SpacetimeVolume model without territory
    """

    class Meta:
        model = SpacetimeVolume
        exclude = ("territory",)


class TerritorialEntitySerializer(ModelSerializer):
    """
    Serializes the TerritorialEntity model
    """

    stvs = SpacetimeVolumeSerializerNoTerritory(many=True, read_only=True)
    stv_count = IntegerField(read_only=True)

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


class CitySerializer(ModelSerializer):
    """
    Serializes the City model
    """

    class Meta:
        model = City
        fields = "__all__"


class SpacetimeVolumeSerializer(ModelSerializer):
    """
    Serializes the SpacetimeVolume model
    """

    class Meta:
        model = SpacetimeVolume
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

    attached_events = CachedDataSerializer(many=True, read_only=True)
    attached_events_ids = PrimaryKeyRelatedField(
        source="attached_events",
        queryset=CachedData.objects.all(),
        many=True,
        write_only=True,
    )

    class Meta:
        model = Narration
        fields = "__all__"


class NarrativeSerializer(ModelSerializer):
    """
    Serializes the Narrative model
    """

    start_year = SerializerMethodField()
    end_year = SerializerMethodField()
    votes = SerializerMethodField()
    narration_count = SerializerMethodField()

    class Meta:
        model = Narrative
        fields = "__all__"

    def get_start_year(self, obj):  # pylint: disable=R0201
        """
        Retrieves year of first narration in set
        """

        if obj.narration_set.first() is not None:
            return jd2gcal(obj.narration_set.first().map_datetime, 0)[0]
        return None

    def get_end_year(self, obj):  # pylint: disable=R0201
        """
        Retrieves year of last narration in set
        """

        if obj.narration_set.last() is not None:
            return jd2gcal(obj.narration_set.last().map_datetime, 0)[0]
        return None

    def get_votes(self, obj):  # pylint: disable=R0201
        """
        Returns dict of upvotes and downvotes
        """

        qs = NarrativeVote.objects.filter(narrative=obj)
        upvotes = qs.aggregate(upvotes=Count(Case(When(vote=True, then=1))))
        downvotes = qs.aggregate(downvotes=Count(Case(When(vote=False, then=1))))
        return {**upvotes, **downvotes}

    def get_narration_count(self, obj):  # pylint: disable=R0201
        """
        Returns count of narrations
        """

        return obj.narration_set.count()
