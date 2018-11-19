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

from .models import DirectPoliticalRelation, IndirectPoliticalRelation

# Create your tests here.
class ModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Create basic model instances
        """
        pass

    def test_model_can_create_directpoliticalrelation(self):
        polrel = DirectPoliticalRelation.objects.create(start_date="0004-01-02", end_date="0006-12-31")
        # we need to do a full refresh to get the value of the path
        polrel.refresh_from_db()
        print(polrel.path)

        assert polrel.id > 0


