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

import factory
from django.contrib.auth.models import User
from .models import (
    TerritorialEntity,
    PoliticalRelation,
    CachedData,
    SpacetimeVolume,
    Narrative,
    NarrativeVote,
    MapSettings,
    Narration,
    City,
)


class TerritorialEntityFactory(factory.django.DjangoModelFactory):
    """
    Factory for the TerritorialEntity model
    """

    class Meta:  # pylint: disable=C0111
        model = TerritorialEntity


class PoliticalRelationFactory(factory.django.DjangoModelFactory):
    """
    Factory for the PoliticalRelation model
    """

    class Meta:  # pylint: disable=C0111
        model = PoliticalRelation


class CachedDataFactory(factory.django.DjangoModelFactory):
    """
    Factory for the CachedData model
    """

    class Meta:  # pylint: disable=C0111
        model = CachedData


class SpacetimeVolumeFactory(factory.django.DjangoModelFactory):
    """
    Factory for the SpacetimeVolume model
    """

    class Meta:  # pylint: disable=C0111
        model = SpacetimeVolume


class NarrativeFactory(factory.django.DjangoModelFactory):
    """
    Factory for the Narrative model
    """

    class Meta:  # pylint: disable=C0111
        model = Narrative


class NarrativeVoteFactory(factory.django.DjangoModelFactory):
    """
    Factory for the NarrativeVote model
    """

    class Meta:  # pylint: disable=C0111
        model = NarrativeVote


class MapSettingsFactory(factory.django.DjangoModelFactory):
    """
    Factory for the MapSettings model
    """

    class Meta:  # pylint: disable=C0111
        model = MapSettings


class NarrationFactory(factory.django.DjangoModelFactory):
    """
    Factory for the Narration model
    """

    class Meta:  # pylint: disable=C0111
        model = Narration


class CityFactory(factory.django.DjangoModelFactory):
    """
    Factory for the City model
    """

    class Meta:  # pylint: disable=C0111
        model = City


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for the django User model
    """

    class Meta:  # pylint: disable=C0111
        model = User
