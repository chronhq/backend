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
from django.test import TestCase

from .factories import TerritorialEntityFactory
from .models import PoliticalRelation, TerritorialEntity

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
        cls.nato = TerritorialEntityFactory(
            wikidata_id=11, color=1, admin_level=1
        )

        cls.germany = TerritorialEntityFactory(wikidata_id=20, color=1, admin_level=2)
        cls.france = TerritorialEntityFactory(wikidata_id=21, color=1, admin_level=2)
        cls.spain = TerritorialEntityFactory(wikidata_id=22, color=1, admin_level=2)
        cls.italy = TerritorialEntityFactory(wikidata_id=23, color=1, admin_level=2)
        cls.british_empire = TerritorialEntityFactory(wikidata_id=24, color=1, admin_level=2)
        cls.british_hk = TerritorialEntityFactory(wikidata_id=25, color=1, admin_level=2)

        cls.alsace = TerritorialEntityFactory(wikidata_id=30, color=1, admin_level=3)
        cls.lorraine = TerritorialEntityFactory(wikidata_id=31, color=1, admin_level=3)

    def test_model_can_create_te(self):
        """
        Ensure that we can create TerritorialEntity
        """
        test_te = TerritorialEntity.objects.create(
            wikidata_id=9,
            color=2,
            admin_level=4
        )
        test_te.save()
        self.assertTrue(TerritorialEntity.objects.filter(wikidata_id=9).exists())

    def test_model_can_create_pr(self):
        """
        Ensure that we can create PoliticalRelation of type GROUP
        """
        france_in_european_union = PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
            parent=self.european_union,
            child=self.france,
            control_type=PoliticalRelation.GROUP,
        )
        germany_in_european_union = PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
            parent=self.european_union,
            child=self.germany,
            control_type=PoliticalRelation.GROUP,
        )
        france_in_nato = PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
            parent=self.nato,
            child=self.france,
            control_type=PoliticalRelation.GROUP,
        )
        self.assertEqual(
            PoliticalRelation.objects.filter(
                parent=self.european_union,
            ).count(),
            2
        )
        self.assertEqual(
            PoliticalRelation.objects.filter(
                parent=self.nato,
            ).count(),
            1
        )

        """
        Ensure that we can create PoliticalRelation of type DIRECT
        """
        alsace_in_france = PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
            parent=self.france,
            child=self.alsace,
            control_type=PoliticalRelation.DIRECT,
        )
        lorraine_in_france = PoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0002-01-01",
            parent=self.france,
            child=self.lorraine,
            control_type=PoliticalRelation.DIRECT,
        )
        self.assertEqual(
            PoliticalRelation.objects.filter(
                parent=self.france,
            ).count(),
            2
        )

        """
        Ensure get_parents is correct
        """
        self.assertEqual(self.lorraine.get_parents().count(), 1)
        self.assertEqual(self.lorraine.get_parents().first(), self.france)
        self.assertEqual(self.france.get_parents().count(), 2) # euopean_union and nato
        self.assertFalse(self.european_union.get_parents().exists())

        """
        Ensure get_children is correct
        """
        self.assertEqual(self.european_union.get_children().count(), 2) # france and germany
        self.assertEqual(self.france.get_children().count(), 2) # alsace and lorraine
        self.assertFalse(self.lorraine.get_children().exists())

    def test_model_can_not_create_pr(self):
        """
        Ensure date checks work
        """
        with self.assertRaises(ValidationError):
            PoliticalRelation.objects.create(
                start_date="0005-01-01",
                end_date="0002-01-01",
                parent=self.european_union,
                child=self.germany,
                control_type=PoliticalRelation.GROUP,
            )
