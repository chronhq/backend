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

# import os
# import requests
from unittest.mock import patch
from django.contrib.gis.geos import Point, Polygon
# from firebase_admin import auth
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
from api.models import (
    PoliticalRelation,
    CachedData,
)

from .test_data import set_up_data

class FakeUser():
    """
    Fake user for drf-firebase-auth
    """

    email="user@example.com"
    email_verified=False
    phone_number="+15555550100"
    password="secretPassword"
    display_name="John Doe"
    disabled=False
    uid="MyFakeUID"
    provider_data = []

firebase_user = FakeUser()

# Helpers
def authorized(function):
    """
    Decorator to mock firebase auth
    """
    def wrapper(*args):
        with patch('drf_firebase_auth.authentication.firebase_auth') as firebase_auth:
            firebase_auth.get_user.return_value = firebase_user
            return function(args[0])
    return wrapper

# def memoize(function):  # https://stackoverflow.com/a/815160/
#     """
#     Decorator to memoize a function return value
#     """
#     memo = {}

#     def wrapper(*args):
#         if args in memo:
#             return memo[args]
#         new_func = function(*args)
#         memo[args] = new_func
#         return new_func

#     return wrapper


# @memoize
# def get_user_token(uid):
#     """
#     Returns an idToken for a given UID
#     """
#     custom_token = auth.create_custom_token(uid)
#     token_req = requests.post(
#         (
#             "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key="
#             f"{os.environ.get('CLIENT_API_KEY')}"
#         ),
#         json={"token": str(custom_token.decode("UTF-8")), "returnSecureToken": True},
#     ).json()
#     return token_req["idToken"]


# Tests
class APITest(APITestCase):
    """
    Tests operations through the API
    """

    def setUp(self):
        """
        Authenticate with firebase_user
        """
        self.client.credentials(
            # HTTP_AUTHORIZATION="JWT " + get_user_token(self.firebase_user)
            HTTP_AUTHORIZATION="JWT MyMockedToken"
        )

    @classmethod
    @authorized
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
        # cls.firebase_user = dict(
        #     email="user@example.com",
        #     email_verified=False,
        #     phone_number="+15555550100",
        #     password="secretPassword",
        #     display_name="John Doe",
        #     disabled=False,
        # )
        # cls.firebase_user = new_firebase_user.uid
        cls.django_user = UserFactory(username="django_user", password="p@55w0rd1")

        # NarrativeVotes
        cls.norman_conquest_vote = NarrativeVoteFactory(
            narrative=cls.norman_conquest, user=cls.django_user, vote=True
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
            wikidata_id=1, label="Paris", location=Point(0, 0), inception_date=cls.JD_0001
        )

    @classmethod
    def tearDownClass(cls):
        """
        Delete test user
        """
        # auth.delete_user(cls.firebase_user)
        super().tearDownClass()
