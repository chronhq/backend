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
from .models import PoliticalRelation

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
            wikidata_id=1, color=1, admin_level=1
        )
        cls.germany = TerritorialEntityFactory(wikidata_id=2, color=1, admin_level=2)
        cls.france = TerritorialEntityFactory(wikidata_id=3, color=1, admin_level=2)
        cls.spain = TerritorialEntityFactory(wikidata_id=4, color=1, admin_level=2)
        cls.italy = TerritorialEntityFactory(wikidata_id=5, color=1, admin_level=2)

    def test_model_can_not_create_polrel(self):
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
