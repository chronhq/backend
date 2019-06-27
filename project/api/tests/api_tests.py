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

import os
from math import ceil
import requests
from django.contrib.gis.geos import Point, Polygon
from django.urls import reverse
from django.test import tag
from firebase_admin import auth
from rest_framework import status
from rest_framework.test import APITestCase
from jdcal import gcal2jd

from api.factories import (
    TerritorialEntityFactory,
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
    TerritorialEntity,
    SpacetimeVolume,
    Narrative,
    NarrativeVote,
    MapSettings,
    Narration,
    CachedData,
    City,
)

# Constants
JD_0001 = ceil(sum(gcal2jd(1, 1, 1))) + 0.0
JD_0002 = ceil(sum(gcal2jd(2, 1, 1))) + 0.0
JD_0003 = ceil(sum(gcal2jd(3, 1, 1))) + 0.0
JD_0004 = ceil(sum(gcal2jd(4, 1, 1))) + 0.0
JD_0005 = ceil(sum(gcal2jd(5, 1, 1))) + 0.0

# Helpers
def memoize(function):  # https://stackoverflow.com/a/815160/
    """
    Decorator to memoize a function return value
    """
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        new_func = function(*args)
        memo[args] = new_func
        return new_func

    return wrapper


@memoize
def get_user_token(uid):
    """
    Returns an idToken for a given UID
    """
    custom_token = auth.create_custom_token(uid)
    token_req = requests.post(
        (
            "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key="
            f"{os.environ.get('CLIENT_API_KEY')}"
        ),
        json={"token": str(custom_token.decode("UTF-8")), "returnSecureToken": True},
    ).json()
    return token_req["idToken"]


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
            HTTP_AUTHORIZATION="JWT " + get_user_token(self.firebase_user)
        )

    @classmethod
    def setUpTestData(cls):
        """
        Create basic model instances
        """

        # TerritorialEntities
        cls.european_union = TerritorialEntityFactory(
            wikidata_id=10,
            label="European Union",
            color=1,
            admin_level=1,
            inception_date=0,
            dissolution_date=1,
        )
        cls.nato = TerritorialEntityFactory(
            wikidata_id=11,
            label="NATO",
            color=1,
            admin_level=1,
            inception_date=0,
            dissolution_date=1,
        )

        cls.germany = TerritorialEntityFactory(
            wikidata_id=20,
            label="Germany",
            color=1,
            admin_level=2,
            inception_date=0,
            dissolution_date=1,
        )
        cls.france = TerritorialEntityFactory(
            wikidata_id=21,
            label="France",
            color=1,
            admin_level=2,
            inception_date=0,
            dissolution_date=1,
        )
        cls.spain = TerritorialEntityFactory(
            wikidata_id=22,
            label="Spain",
            color=1,
            admin_level=2,
            inception_date=0,
            dissolution_date=1,
        )
        cls.italy = TerritorialEntityFactory(
            wikidata_id=23,
            label="Italy",
            color=1,
            admin_level=2,
            inception_date=0,
            dissolution_date=1,
        )
        cls.british_empire = TerritorialEntityFactory(
            wikidata_id=24,
            label="British Empire",
            color=1,
            admin_level=2,
            inception_date=0,
            dissolution_date=1,
        )
        cls.british_hk = TerritorialEntityFactory(
            wikidata_id=25,
            label="British HK",
            color=1,
            admin_level=2,
            inception_date=0,
            dissolution_date=1,
        )

        cls.alsace = TerritorialEntityFactory(
            wikidata_id=30,
            label="Alsace",
            color=1,
            admin_level=3,
            inception_date=0,
            dissolution_date=1,
        )
        cls.lorraine = TerritorialEntityFactory(
            wikidata_id=31,
            label="Lorraine",
            color=1,
            admin_level=3,
            inception_date=0,
            dissolution_date=1,
        )

        # PoliticalRelations
        cls.EU_germany = PoliticalRelationFactory(
            parent=cls.european_union,
            child=cls.germany,
            start_date=JD_0001,
            end_date=JD_0002,
            control_type=PoliticalRelation.INDIRECT,
        )

        # CachedData
        cls.hastings = CachedDataFactory(
            wikidata_id=1,
            location=Point(0, 0),
            date=JD_0001,
            event_type=CachedData.BATTLE,
        )

        # SpacetimeVolumes
        cls.alsace_stv = SpacetimeVolumeFactory(
            start_date=JD_0001,
            end_date=JD_0002,
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
        new_firebase_user = auth.create_user(
            email="user@example.com",
            email_verified=False,
            phone_number="+15555550100",
            password="secretPassword",
            display_name="John Doe",
            disabled=False,
        )
        cls.firebase_user = new_firebase_user.uid
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
            map_datetime=JD_0002,
            settings=cls.norman_conquest_settings,
            location=Point(0, 0),
        )

        # Cities
        cls.paris = CityFactory(
            wikidata_id=1, label="Paris", location=Point(0, 0), inception_date=JD_0001
        )

    def test_api_can_create_te(self):
        """
        Ensure we can create TerritorialEntities
        """

        url = reverse("territorialentity-list")
        data = {
            "wikidata_id": 9,
            "label": "Test TE",
            "color": "#fff",
            "admin_level": 4,
            "inception_date": 0,
            "dissolution_date": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TerritorialEntity.objects.count(), 11)
        self.assertEqual(TerritorialEntity.objects.last().admin_level, 4)

    def test_api_can_update_te(self):
        """
        Ensure we can update TerritorialEntities
        """

        url = reverse("territorialentity-detail", args=[self.european_union.pk])
        data = {
            "wikidata_id": 10,
            "label": "Update",
            "color": "#fff",
            "admin_level": 5,
            "inception_date": 0,
            "dissolution_date": 1,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["admin_level"], 5)

    def test_api_can_query_tes(self):
        """
        Ensure we can query for all TerritorialEntities
        """

        url = reverse("territorialentity-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.european_union.pk)
        self.assertEqual(response.data[3]["stv_count"], 1)

    def test_api_can_query_te(self):
        """
        Ensure we can query for individual TerritorialEntities
        """

        url = reverse("territorialentity-detail", args=[self.european_union.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["admin_level"], 1)

    def test_api_can_create_pr(self):
        """
        Ensure we can create PoliticalRelations
        """

        url = reverse("politicalrelation-list")
        data = {
            "start_date": JD_0001,
            "end_date": JD_0002,
            "parent": self.european_union.pk,
            "child": self.france.pk,
            "control_type": PoliticalRelation.GROUP,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PoliticalRelation.objects.count(), 2)
        self.assertEqual(
            PoliticalRelation.objects.last().control_type, PoliticalRelation.GROUP
        )

    def test_api_can_update_pr(self):
        """
        Ensure we can update PoliticalRelations
        """

        url = reverse("politicalrelation-detail", args=[self.EU_germany.pk])
        data = {
            "start_date": JD_0001,
            "end_date": JD_0002,
            "parent": self.european_union.pk,
            "child": self.france.pk,
            "control_type": PoliticalRelation.GROUP,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["control_type"], PoliticalRelation.GROUP)

    def test_api_can_query_prs(self):
        """
        Ensure we can query for all PoliticalRelations
        """

        url = reverse("politicalrelation-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["control_type"], PoliticalRelation.INDIRECT)

    def test_api_can_query_pr(self):
        """
        Ensure we can query for individual PoliticalRelations
        """

        url = reverse("politicalrelation-detail", args=[self.EU_germany.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["control_type"], PoliticalRelation.INDIRECT)

    def test_api_can_create_cd(self):
        """
        Ensure we can create CachedData
        """

        url = reverse("cacheddata-list")
        data = {
            "wikidata_id": 2,
            "location": "Point(0 1)",
            "date": JD_0001,
            "event_type": CachedData.DOCUMENT,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CachedData.objects.count(), 2)
        self.assertEqual(CachedData.objects.last().event_type, CachedData.DOCUMENT)

    def test_api_can_create_cd_othertype(self):
        """
        Ensure we can create CachedData with an event_type not in the choices
        """

        url = reverse("cacheddata-list")
        data = {
            "wikidata_id": 2,
            "location": "Point(0 1)",
            "date": JD_0001,
            "event_type": 555,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CachedData.objects.count(), 2)
        self.assertEqual(CachedData.objects.last().event_type, 555)

    def test_api_can_update_cd(self):
        """
        Ensure we can update CachedData
        """

        url = reverse("cacheddata-detail", args=[self.hastings.pk])
        data = {
            "wikidata_id": 1,
            "location": "Point(0 0)",
            "date": JD_0001,
            "event_type": CachedData.DOCUMENT,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["event_type"], CachedData.DOCUMENT)

    def test_api_can_query_cds(self):
        """
        Ensure we can query for all CachedDatas
        """

        url = reverse("cacheddata-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["event_type"], CachedData.BATTLE)

    def test_api_can_query_cd(self):
        """
        Ensure we can query for individual CachedDatas
        """

        url = reverse("cacheddata-detail", args=[self.hastings.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["event_type"], CachedData.BATTLE)

    def test_api_can_create_stv(self):
        """
        Ensure we can create SpacetimeVolumes
        """

        url = reverse("spacetimevolume-list")
        data = {
            "start_date": JD_0001,
            "end_date": JD_0002,
            "entity": self.germany.pk,
            "references": ["ref"],
            "territory": "POLYGON((3 3, 3 4, 4 4, 3 3))",
            "visual_center": "POINT(1.2 1.8)",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SpacetimeVolume.objects.count(), 2)
        self.assertEqual(SpacetimeVolume.objects.last().references, ["ref"])

    def test_api_can_update_stv(self):
        """
        Ensure we can update SpacetimeVolumes
        """

        url = reverse("spacetimevolume-detail", args=[self.alsace_stv.pk])
        data = {
            "start_date": JD_0001,
            "end_date": JD_0005,
            "entity": self.france.pk,
            "references": ["ref"],
            "territory": "POLYGON((1 1, 1 2, 2 2, 1 1))",
            "visual_center": "POINT (0.7 0.7)",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["end_date"], str(JD_0005))

    def test_api_can_query_stv(self):
        """
        Ensure we can query for individual SpacetimeVolumes
        """

        url = reverse("spacetimevolume-detail", args=[self.alsace_stv.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["end_date"], str(JD_0002))

    def test_api_can_create_narrative(self):
        """
        Ensure we can create Narratives
        """

        url = reverse("narrative-list")
        data = {
            "author": "Test Author 2",
            "title": "Test Narrative",
            "url": "test2",
            "description": "This is a test narrative for automated testing.",
            "tags": ["test", "tags"],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Narrative.objects.count(), 2)
        self.assertEqual(Narrative.objects.last().author, "Test Author 2")

    def test_api_can_update_narrative(self):
        """
        Ensure we can update Narratives
        """

        url = reverse("narrative-detail", args=[self.norman_conquest.pk])
        data = {
            "author": "Other Test Author",
            "title": "Test Narrative",
            "url": "test2",
            "description": "This is a test narrative for automated testing.",
            "tags": ["test", "tags"],
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["author"], "Other Test Author")

    def test_api_can_query_narratives(self):
        """
        Ensure we can query for all Narratives
        """

        url = reverse("narrative-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["author"], "Test Author")

    def test_api_can_query_narrative(self):
        """
        Ensure we can query for individual Narratives
        """

        url = reverse("narrative-detail", args=[self.norman_conquest.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["author"], "Test Author")

    @tag("new")
    def test_api_can_query_narrative_votes(self):
        """
        Ensure upvotes and downvotes are being returned correctly
        """

        url = reverse("narrative-detail", args=[self.norman_conquest.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["votes"], {"upvotes": 1, "downvotes": 0})

    def test_api_can_create_ms(self):
        """
        Ensure we can create MapSettings
        """

        url = reverse("mapsettings-list")
        data = {"zoom_min": 1, "zoom_max": 13}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MapSettings.objects.count(), 2)
        self.assertEqual(MapSettings.objects.last().zoom_min, 1.0)

    def test_api_can_update_ms(self):
        """
        Ensure we can update MapSettings
        """

        url = reverse("mapsettings-detail", args=[self.norman_conquest_settings.pk])
        data = {"zoom_min": 5, "zoom_max": 13}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["zoom_min"], 5)

    def test_api_can_query_mss(self):
        """
        Ensure we can query for all MapSettings
        """

        url = reverse("mapsettings-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["zoom_min"], 1)

    def test_api_can_query_ms(self):
        """
        Ensure we can query for individual MapSettings
        """

        url = reverse("mapsettings-detail", args=[self.norman_conquest_settings.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["zoom_min"], 1)

    def test_api_can_create_narration(self):
        """
        Ensure we can create Narrations
        """

        url = reverse("narration-list")
        data = {
            "narrative": self.norman_conquest.pk,
            "title": "Test Narration",
            "description": "This is a narration point",
            "date_label": "test",
            "map_datetime": JD_0002,
            "settings": self.norman_conquest_settings.pk,
            "attached_events_ids": [self.hastings.pk],
            "location": "POINT (0 0)",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Narration.objects.count(), 2)
        self.assertEqual(Narration.objects.last().title, "Test Narration")

    def test_api_can_update_narration(self):
        """
        Ensure we can update Narrations
        """

        url = reverse("narration-detail", args=[self.hastings_narration.pk])
        data = {
            "narrative": self.norman_conquest.pk,
            "title": "Test Narration 2",
            "description": "This is a narration point",
            "date_label": "test",
            "map_datetime": JD_0002,
            "settings": self.norman_conquest_settings.pk,
            "attached_events_ids": [self.hastings.pk],
            "location": "POINT (0 0)",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Narration 2")

    def test_api_can_query_narrations(self):
        """
        Ensure we can query for all Narrations
        """

        url = reverse("narration-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Test Narration")

    def test_api_can_query_narration(self):
        """
        Ensure we can query for individual Narrations
        """

        url = reverse("narration-detail", args=[self.hastings_narration.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Narration")

    def test_api_can_create_city(self):
        """
        Ensure we can create Cities
        """

        url = reverse("city-list")
        data = {
            "wikidata_id": 2,
            "label": "London",
            "location": "POINT (10 10)",
            "inception_date": JD_0001,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), 2)
        self.assertEqual(City.objects.last().label, "London")

    def test_api_can_update_city(self):
        """
        Ensure we can update Cities
        """

        url = reverse("city-detail", args=[self.paris.pk])
        data = {
            "wikidata_id": 2,
            "label": "London",
            "location": "POINT (10 10)",
            "inception_date": JD_0001,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], "London")

    def test_api_can_query_cities(self):
        """
        Ensure we can query for all Cities
        """

        url = reverse("city-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["label"], "Paris")

    def test_api_can_query_city(self):
        """
        Ensure we can query for individual Cities
        """

        url = reverse("city-detail", args=[self.paris.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], "Paris")

    def test_api_can_create_narrativevote(self):
        """
        Ensure we can vote on Narratives
        """

        url = reverse("narrativevote-list")
        data = {
            "narrative": self.norman_conquest.pk,
            "user": self.django_user.pk,
            "vote": 0,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NarrativeVote.objects.count(), 1)
        self.assertEqual(NarrativeVote.objects.last().vote, 0)

    def test_api_can_update_narrativevote(self):
        """
        Ensure we can change our NarrativeVotes
        """

        url = reverse("narrativevote-list")
        data = {
            "narrative": self.norman_conquest.pk,
            "user": self.django_user.pk,
            "vote": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NarrativeVote.objects.count(), 1)
        self.assertEqual(NarrativeVote.objects.last().vote, 1)

    def test_api_can_query_narrativevotes(self):
        """
        Ensure we can query for all NarrativeVotes
        """

        url = reverse("narrativevote-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["vote"], True)

    def test_api_can_query_narrativevote(self):
        """
        Ensure we can query for individual NarrativeVotes
        """

        url = reverse("narrativevote-detail", args=[self.norman_conquest_vote.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["vote"], True)

    def test_api_can_remove_narrativevote(self):
        """
        Ensure we can remove our NarrativeVote
        """

        url = reverse("narrativevote-list")
        data = {
            "narrative": self.norman_conquest.pk,
            "user": self.django_user.pk,
            "vote": None,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(NarrativeVote.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_can_not_update_profile(self):
        """
        Ensure Profile permissions are operational
        """

        url = reverse("profile-detail", args=[self.django_user.profile.pk])
        data = {"location": "POINT (10 10)"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_can_update_profile(self):
        """
        Ensure user's own Profile can be updated
        """

        url = reverse("profile-detail", args=[self.django_user.profile.pk])
        data = {"location": "POINT (10 10)"}
        self.client.force_authenticate(user=self.django_user)
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["location"]["coordinates"], [10.0, 10.0])

    def test_api_can_query_profiles(self):
        """
        Ensure we can query for all Profiles
        """

        url = reverse("profile-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["user"], self.django_user.pk)

    def test_api_can_query_profile(self):
        """
        Ensure we can query for individual Profiles
        """

        url = reverse("profile-detail", args=[self.django_user.profile.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.django_user.pk)

    @classmethod
    def tearDownClass(cls):
        """
        Delete test user
        """
        auth.delete_user(cls.firebase_user)
        super().tearDownClass()
