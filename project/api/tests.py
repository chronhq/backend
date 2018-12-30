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

from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point, Polygon, MultiPoint
from django.test import TestCase

from .factories import TerritorialEntityFactory, AtomicPolygonFactory
from .models import (
    PoliticalRelation,
    TerritorialEntity,
    AtomicPolygon,
    SpacetimeVolume,
    Narrative,
    MapSettings,
    Narration,
    CachedData,
)

# Create your tests here.
class ModelTest(TestCase):
    """
    Tests model constraints directly
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create basic model instances
        """

        cls.european_union = TerritorialEntityFactory(
            wikidata_id=10, color=1, admin_level=1
        )
        cls.nato = TerritorialEntityFactory(wikidata_id=11, color=1, admin_level=1)

        cls.germany = TerritorialEntityFactory(wikidata_id=20, color=1, admin_level=2)
        cls.france = TerritorialEntityFactory(wikidata_id=21, color=1, admin_level=2)
        cls.spain = TerritorialEntityFactory(wikidata_id=22, color=1, admin_level=2)
        cls.italy = TerritorialEntityFactory(wikidata_id=23, color=1, admin_level=2)
        cls.british_empire = TerritorialEntityFactory(
            wikidata_id=24, color=1, admin_level=2
        )
        cls.british_hk = TerritorialEntityFactory(
            wikidata_id=25, color=1, admin_level=2
        )

        cls.alsace = TerritorialEntityFactory(wikidata_id=30, color=1, admin_level=3)
        cls.lorraine = TerritorialEntityFactory(wikidata_id=31, color=1, admin_level=3)

        cls.alsace_geom = AtomicPolygonFactory.create(
            name="Alsace", geom=Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))
        )

    def test_model_can_create_te(self):
        """
        Ensure that we can create TerritorialEntity
        """

        test_te = TerritorialEntity.objects.create(
            wikidata_id=9, color=2, admin_level=4
        )
        test_te.save()
        self.assertTrue(TerritorialEntity.objects.filter(wikidata_id=9).exists())

    def test_model_can_create_pr(self):
        """
        Ensure that we can create PoliticalRelations of types GROUP and DIRECT
        Tests get_children() and get_parents() methods
        """

        # GROUP
        PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
            parent=self.european_union,
            child=self.france,
            control_type=PoliticalRelation.GROUP,
        )
        PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
            parent=self.european_union,
            child=self.germany,
            control_type=PoliticalRelation.GROUP,
        )
        PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
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
            start_date="0001-01-01",
            end_date="0002-01-01",
            parent=self.france,
            child=self.alsace,
            control_type=PoliticalRelation.DIRECT,
        )
        PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
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
                start_date="0005-01-01",
                end_date="0002-01-01",
                parent=self.european_union,
                child=self.germany,
                control_type=PoliticalRelation.GROUP,
            )

        with self.assertRaises(ValidationError):
            PoliticalRelation.objects.create(
                start_date="0001-01-01",
                end_date="0002-01-01",
                parent=self.germany,
                child=self.european_union,
                control_type=PoliticalRelation.DIRECT,
            )

    def test_model_can_create_ap(self):
        """
        Ensure we can create AtomicPolygons
        """

        AtomicPolygon.objects.create(
            name="Lorraine", geom=Polygon(((3, 3), (3, 4), (4, 4), (3, 3)))
        )

        self.assertEqual(AtomicPolygon.objects.count(), 2)

    def test_model_can_not_create_ap(self):
        """
        Ensure the AtomicPolygon validations work
        """

        # Geometry type validation
        with self.assertRaises(ValidationError):
            AtomicPolygon.objects.create(name="Lorraine", geom=Point(2.5, 2.5))

        # Non overlapping childless AP constraint
        with self.assertRaises(ValidationError):
            AtomicPolygon.objects.create(
                name="Lorraine", geom=Polygon(((1, 1), (1, 3), (2, 2), (1, 1)))
            )

    def test_model_can_create_stv(self):
        """
        Ensure we can create SpacetimeVolumes
        """

        alsace = SpacetimeVolume.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
            entity=self.france,
            references=["ref"],
        )
        alsace.territory.add(self.alsace_geom)

        self.assertTrue(
            SpacetimeVolume.objects.filter(territory__in=[self.alsace_geom]).exists()
        )

    def test_model_can_not_create_stv(self):
        """
        Ensure non overlapping timeframe constraint works
        """

        with self.assertRaises(ValidationError):
            SpacetimeVolume.objects.create(
                start_date="0001-01-01",
                end_date="0003-01-01",
                entity=self.france,
                references=["ref"],
            )
            SpacetimeVolume.objects.create(
                start_date="0002-01-01",
                end_date="0004-01-01",
                entity=self.france,
                references=["ref"],
            )

    def test_model_can_create_narrative(self):
        """
        Ensure that we can create a narrative and the ordering plugin works.
        """
        test_narrative = Narrative.objects.create(
            author="Test Author",
            title="Test Narrative",
            description="This is a test narrative for automated testing.",
            tags=["test", "tags"],
        )

        test_settings = MapSettings.objects.create(
            bbox=MultiPoint(Point(0, 0), Point(1, 1)), zoom_min=1, zoom_max=12
        )

        hastings = CachedData.objects.create(
            wikidata_id=1,
            location=Point(0, 0),
            date="0001-01-01",
            event_type=CachedData.BATTLE,
        )

        balaclava = CachedData.objects.create(
            wikidata_id=2,
            location=Point(0, 0),
            date="0002-02-02",
            event_type=CachedData.BATTLE,
        )

        narration1 = Narration.objects.create(
            narrative=test_narrative,
            title="Test Narration",
            description="This is a narration point",
            date_label="test",
            map_datetime="0002-01-01 00:00",
            settings=test_settings,
        )

        narration1.attached_events.add(hastings)

        test_settings2 = MapSettings.objects.create(
            bbox=MultiPoint(Point(0, 0), Point(1, 1)), zoom_min=1, zoom_max=12
        )

        narration2 = Narration.objects.create(
            narrative=test_narrative,
            title="Test Narration2",
            description="This is another narration point",
            date_label="test2",
            map_datetime="0002-05-01 00:00",
            settings=test_settings2,
        )

        narration2.attached_events.add(balaclava)

        narration1.swap(narration2)

        self.assertEqual(Narrative.objects.filter().count(), 1)
        self.assertEqual(Narration.objects.filter().count(), 2)
        self.assertEqual(narration2.next().title, "Test Narration")

    def test_model_cant_create_bbox(self):
        """
        Ensure that the constraints on mapsettings work.
        """

        with self.assertRaises(ValidationError):
            MapSettings.objects.create(
                bbox=MultiPoint(Point(0, 0)), zoom_min=1, zoom_max=2
            )

        with self.assertRaises(ValidationError):
            MapSettings.objects.create(
                bbox=MultiPoint(Point(0, 0), Point(1, 1), Point(0, 1)),
                zoom_min=1,
                zoom_max=2,
            )

        with self.assertRaises(ValidationError):
            MapSettings.objects.create(
                bbox=MultiPoint(Point(0, 0), Point(1, 1)), zoom_min=-0.1, zoom_max=2
            )

        with self.assertRaises(ValidationError):
            MapSettings.objects.create(
                bbox=MultiPoint(Point(0, 0), Point(1, 1)), zoom_min=1, zoom_max=22.1
            )

        with self.assertRaises(ValidationError):
            MapSettings.objects.create(
                bbox=MultiPoint(Point(0, 0), Point(1, 1)), zoom_min=5, zoom_max=3
            )

    def test_model_can_create_cd(self):
        """
        Ensure CachedData can be created
        """

        hastings = CachedData.objects.create(
            wikidata_id=1,
            location=Point(0, 0),
            date="0001-01-01",
            event_type=CachedData.BATTLE,
        )

        self.assertTrue(hastings.rank > 0, hastings.date)
        self.assertEqual(CachedData.objects.count(), 1)
