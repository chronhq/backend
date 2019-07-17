# pylint: disable=C0302

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

from unittest.mock import patch
from django.contrib.gis.geos import Point, Polygon
from django.utils.crypto import get_random_string
from rest_framework.test import APITestCase

from api.factories import (
    PoliticalRelationFactory,
    CachedDataFactory,
    SpacetimeVolumeFactory,
    NarrativeFactory,
    NarrativeVoteFactory,
    MapSettingsFactory,
    NarrationFactory,
    CityFactory,
    UserFactory,
)
from api.models import PoliticalRelation, CachedData

from .test_data import set_up_data, wiki_cd


class FakeUser:  # pylint: disable=too-few-public-methods
    """
    Fake user for drf-firebase-auth
    """

    email = "user@example.com"
    email_verified = False
    phone_number = "+15555550100"
    password = get_random_string(length=16)
    display_name = "John Doe"
    disabled = False
    uid = "MyFakeUID"
    provider_data = []


FIREBASE_USER = FakeUser()

# Helpers
def authorized(function):
    """
    Decorator to mock firebase auth
    """

    def wrapper(*args):
        with patch("drf_firebase_auth.authentication.firebase_auth") as firebase_auth:
            firebase_auth.get_user.return_value = FIREBASE_USER
            return function(args[0])

    return wrapper


# Tests
class APITest(APITestCase):
    """
    Tests operations through the API
    """

    def setUp(self):
        """
        Authenticate with firebase_user
        """
        self.client.credentials(HTTP_AUTHORIZATION="JWT MyMockedToken")

    @classmethod
    @authorized
    @wiki_cd
    def setUpTestData(cls):
        """
        Create basic model instances
        """

        set_up_data(cls)

        # PoliticalRelations
        cls.EU_germany = PoliticalRelationFactory(
            parent=cls.european_union,
            child=cls.germany,
            start_date=cls.JD_0001,
            end_date=cls.JD_0002,
            control_type=PoliticalRelation.INDIRECT,
        )

        # CachedData
        cls.hastings = CachedDataFactory(
            wikidata_id=1,
            location=Point(0, 0),
            date=cls.JD_0001,
            event_type=CachedData.BATTLE,
        )

        # SpacetimeVolumes
        cls.alsace_stv = SpacetimeVolumeFactory(
            start_date=cls.JD_0001,
            end_date=cls.JD_0002,
            entity=cls.france,
            references=["ref"],
            visual_center=Point(1.2, 1.8),
            territory=Polygon(((1, 1), (1, 2), (2, 2), (1, 1))),
        )

        # Narratives
        cls.norman_conquest = NarrativeFactory(
            author="Test Author",
            title="Test Narrative",
            url="test",
            description="This is a test narrative for automated testing.",
            tags=["test", "tags"],
        )

        # Users
        cls.django_user = UserFactory(
            email=FIREBASE_USER.email,
            username="django_user",
            password=FIREBASE_USER.password,
        )

        cls.test_user = UserFactory(
            email="test@test.com",
            username="test_user",
            password=get_random_string(length=16),
        )

        # NarrativeVotes
        cls.norman_conquest_vote = NarrativeVoteFactory(
            narrative=cls.norman_conquest, user=cls.test_user, vote=True
        )

        # MapSettings
        cls.norman_conquest_settings = MapSettingsFactory(zoom_min=1, zoom_max=12)

        # Narrations
        cls.hastings_narration = NarrationFactory(
            narrative=cls.norman_conquest,
            title="Test Narration",
            description="This is a narration point",
            date_label="test",
            map_datetime=cls.JD_0002,
            settings=cls.norman_conquest_settings,
            location=Point(0, 0),
        )

        # Cities
        cls.paris = CityFactory(
            wikidata_id=1,
            label="Paris",
            location=Point(0, 0),
            inception_date=cls.JD_0001,
        )
