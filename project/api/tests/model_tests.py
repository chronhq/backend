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
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point, Polygon
from django.test import TestCase

# from api.factories import TerritorialEntityFactory

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
    Profile,
)

from .test_data import set_up_data, wiki_cd

# Tests
class ModelTest(TestCase):
    """
    Tests model constraints directly
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create basic model instances
        """
        set_up_data(cls)

    def test_model_can_create_te(self):
        """
        Ensure that we can create TerritorialEntity
        """

        test_te = TerritorialEntity.objects.create(
            wikidata_id=9,
            label="test TE",
            color=2,
            admin_level=4,
            inception_date=0,
            dissolution_date=1,
        )
        test_te.save()
        test_te.predecessor.add(self.alsace)
        self.assertTrue(TerritorialEntity.objects.filter(wikidata_id=9).exists())

    def test_model_can_create_pr(self):
        """
        Ensure that we can create PoliticalRelations of types GROUP and DIRECT
        Tests get_children() and get_parents() methods
        """

        # GROUP
        PoliticalRelation.objects.create(
            start_date=self.JD_0001,
            end_date=self.JD_0002,
            parent=self.european_union,
            child=self.france,
            control_type=PoliticalRelation.GROUP,
        )
        PoliticalRelation.objects.create(
            start_date=self.JD_0001,
            end_date=self.JD_0002,
            parent=self.european_union,
            child=self.germany,
            control_type=PoliticalRelation.GROUP,
        )
        PoliticalRelation.objects.create(
            start_date=self.JD_0001,
            end_date=self.JD_0002,
            parent=self.nato,
            child=self.france,
            control_type=PoliticalRelation.GROUP,
        )
        self.assertEqual(
            PoliticalRelation.objects.filter(parent=self.european_union).count(), 2
        )
        self.assertEqual(PoliticalRelation.objects.filter(parent=self.nato).count(), 1)

        # DIRECT
        PoliticalRelation.objects.create(
            start_date=self.JD_0001,
            end_date=self.JD_0002,
            parent=self.france,
            child=self.alsace,
            control_type=PoliticalRelation.DIRECT,
        )
        PoliticalRelation.objects.create(
            start_date=self.JD_0001,
            end_date=self.JD_0002,
            parent=self.france,
            child=self.lorraine,
            control_type=PoliticalRelation.DIRECT,
        )
        self.assertEqual(
            PoliticalRelation.objects.filter(parent=self.france).count(), 2
        )

        # get_parents()
        self.assertEqual(self.lorraine.get_parents().count(), 1)
        self.assertEqual(self.lorraine.get_parents().first(), self.france)
        self.assertEqual(self.france.get_parents().count(), 2)  # euopean_union and nato
        self.assertFalse(self.european_union.get_parents().exists())

        # get_children()
        self.assertEqual(
            self.european_union.get_children().count(), 2
        )  # france and germany
        self.assertEqual(self.france.get_children().count(), 2)  # alsace and lorraine
        self.assertFalse(self.lorraine.get_children().exists())

    def test_model_can_not_create_pr(self):
        """
        Ensure PoliticalRelation validations work
        """

        with self.assertRaises(ValidationError):
            PoliticalRelation.objects.create(
                start_date=self.JD_0005,
                end_date=self.JD_0002,
                parent=self.european_union,
                child=self.germany,
                control_type=PoliticalRelation.GROUP,
            )

        with self.assertRaises(ValidationError):
            PoliticalRelation.objects.create(
                start_date=self.JD_0001,
                end_date=self.JD_0002,
                parent=self.germany,
                child=self.european_union,
                control_type=PoliticalRelation.DIRECT,
            )

    def test_model_can_create_stv(self):
        """
        Ensure we can create SpacetimeVolumes
        """

        SpacetimeVolume.objects.create(
            start_date=self.JD_0001,
            end_date=self.JD_0002,
            entity=self.france,
            references=["ref"],
            visual_center=Point(1.2, 1.8),
            territory=Polygon(((1, 1), (1, 2), (2, 2), (1, 1))),
        )

        self.assertTrue(
            SpacetimeVolume.objects.filter(
                territory=Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))
            ).exists()
        )

        self.assertEqual(
            str(
                SpacetimeVolume.objects.filter(
                    territory=Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))
                )[0].visual_center
            ),
            "SRID=4326;POINT (1.2 1.8)",
        )

    def test_model_can_not_create_stv(self):
        """
        Ensure non overlapping timeframe and territory constraints works
        """
        # Timeframe
        with self.assertRaises(ValidationError):
            SpacetimeVolume.objects.create(
                start_date=self.JD_0001,
                end_date=self.JD_0003,
                entity=self.france,
                references=["ref"],
                visual_center=Point(2, 2),
                territory=Polygon(((1, 1), (1, 2), (2, 2), (1, 1))),
            )
            SpacetimeVolume.objects.create(
                start_date=self.JD_0002,
                end_date=self.JD_0004,
                entity=self.france,
                references=["ref"],
                visual_center=Point(1, 1),
                territory=Polygon(((3, 3), (3, 4), (4, 4), (3, 3))),
            )

        # Territory
        with self.assertRaises(ValidationError):
            SpacetimeVolume.objects.create(
                start_date=self.JD_0003,
                end_date=self.JD_0004,
                entity=self.british_empire,
                references=["ref"],
                visual_center=Point(2, 2),
                territory=Polygon(((6, 6), (6, 7), (7, 7), (6, 6))),
            )
            SpacetimeVolume.objects.create(
                start_date=self.JD_0002,
                end_date=self.JD_0004,
                entity=self.italy,
                references=["ref"],
                visual_center=Point(1, 1),
                territory=Polygon(((6, 6), (6, 7), (7, 7), (6, 6))),
            )

        # Geom type
        with self.assertRaises(ValidationError):
            SpacetimeVolume.objects.create(
                start_date=self.JD_0001,
                end_date=self.JD_0003,
                entity=self.france,
                references=["ref"],
                visual_center=Point(2, 2),
                territory=Point(1, 1),
            )

    @wiki_cd
    def test_model_can_create_narrative(self):
        """
        Ensure that we can create a narrative and the ordering plugin works.
        """
        test_narrative = Narrative.objects.create(
            author="Test Author",
            title="Test Narrative",
            url="test",
            description="This is a test narrative for automated testing.",
            tags=["test", "tags"],
        )

        test_settings = MapSettings.objects.create(zoom_min=1, zoom_max=12)

        hastings = CachedData.objects.create(
            wikidata_id=1,
            location=Point(0, 0),
            date=self.JD_0001,
            event_type=CachedData.BATTLE,
        )

        balaclava = CachedData.objects.create(
            wikidata_id=2,
            location=Point(0, 0),
            date=self.JD_0002,
            event_type=CachedData.BATTLE,
        )

        narration1 = Narration.objects.create(
            narrative=test_narrative,
            title="Test Narration",
            description="This is a narration point",
            date_label="test",
            map_datetime=self.JD_0002,
            settings=test_settings,
            location=Point(0, 0),
        )

        narration1.attached_events.add(hastings)

        test_settings2 = MapSettings.objects.create(zoom_min=1, zoom_max=12)

        narration2 = Narration.objects.create(
            narrative=test_narrative,
            title="Test Narration2",
            description="This is another narration point",
            date_label="test2",
            map_datetime=self.JD_0002,
            settings=test_settings2,
            location=Point(0, 0),
        )

        narration2.attached_events.add(balaclava)

        narration1.swap(narration2)

        test_user = User.objects.create(
            username="test_user", password=get_random_string(length=16)
        )

        vote1 = NarrativeVote.objects.create(
            narrative=test_narrative, user=test_user, vote=True
        )

        self.assertEqual(Narrative.objects.filter().count(), 1)
        self.assertEqual(Narration.objects.filter().count(), 2)
        self.assertEqual(narration2.next().title, "Test Narration")

        self.assertTrue(vote1.vote)
        self.assertTrue(
            Narrative.objects.first().votes.filter(username=test_user.username).exists()
        )
        self.assertEqual(NarrativeVote.objects.count(), 1)

    def test_model_can_not_create_ms(self):
        """
        Ensure that the constraints on mapsettings work.
        """

        with self.assertRaises(ValidationError):
            MapSettings.objects.create(zoom_min=-0.1, zoom_max=2)

        with self.assertRaises(ValidationError):
            MapSettings.objects.create(zoom_min=1, zoom_max=22.1)

        with self.assertRaises(ValidationError):
            MapSettings.objects.create(zoom_min=5, zoom_max=3)

    @wiki_cd
    def test_model_can_create_cd(self):
        """
        Ensure CachedData can be created
        """

        hastings = CachedData.objects.create(
            wikidata_id=1,
            location=Point(0, 0),
            date=self.JD_0001,
            event_type=CachedData.BATTLE,
        )

        self.assertTrue(hastings.rank >= 0)
        self.assertEqual(hastings.date, self.JD_0001)
        self.assertEqual(CachedData.objects.count(), 1)

    def test_model_can_create_city(self):
        """
        Ensure Cities can be created
        """

        paris = City.objects.create(
            wikidata_id=1,
            label="Paris",
            location=Point(0, 0),
            inception_date=self.JD_0001,
        )

        self.assertEqual(paris.label, "Paris")
        self.assertEqual(City.objects.count(), 1)

    def test_model_can_create_profile(self):
        """
        Ensures Profiles are created on User create
        """
        test_user = User.objects.create_user(
            username="test_user", password="test_password"
        )

        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.first().user, test_user)
