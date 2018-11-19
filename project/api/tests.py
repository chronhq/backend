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

from django.test import TestCase

from .factories import PoliticalEntityFactory
from .models import DirectPoliticalRelation

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
        cls.new_nation = PoliticalEntityFactory(wikidata_id=1, color=1, admin_level=1)

    def test_model_can_create_directpoliticalrelation(self):
        """
        Test if DPR can be created
        """
        dpr = DirectPoliticalRelation.objects.create(
            start_date="0004-01-02", end_date="0006-12-31", entity=self.new_nation
        )
        # we need to do a full refresh to get the value of the path
        dpr.refresh_from_db()

        self.assertTrue(dpr.id > 0)
        self.assertEqual(dpr.entity, self.new_nation)
        self.assertTrue(dpr.path)
