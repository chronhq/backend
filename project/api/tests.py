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

from django.db.utils import IntegrityError
from django.test import TestCase

from .factories import PoliticalEntityFactory
from .models import DirectPoliticalRelation, IndirectPoliticalRelation, PoliticalEntity

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

        cls.european_union = PoliticalEntityFactory(wikidata_id=1, color=1, admin_level=1)
        cls.germany = PoliticalEntityFactory(
            wikidata_id=2, color=1, admin_level=2
        )
        cls.france = PoliticalEntityFactory(
            wikidata_id=3, color=1, admin_level=2
        )
        cls.spain = PoliticalEntityFactory(
            wikidata_id=4, color=1, admin_level=2
        )
        cls.italy = PoliticalEntityFactory(
            wikidata_id=5, color=1, admin_level=2
        )
