# pylint: disable=C0302

"""
Chron.
Copyright (C) 2019 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
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

from rest_framework import status
from django.urls import reverse
from api.models import TerritorialEntity
from .api_tests import APITest, authorized


class TETests(APITest):
    """
    Territorial Entities test suite
    """

    @authorized
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

    @authorized
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

    @authorized
    def test_api_can_query_tes(self):
        """
        Ensure we can query for all TerritorialEntities
        """

        url = reverse("territorialentity-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.european_union.pk)
        self.assertEqual(response.data[3]["stv_count"], 1)

    @authorized
    def test_api_can_query_te(self):
        """
        Ensure we can query for individual TerritorialEntities
        """

        url = reverse("territorialentity-detail", args=[self.european_union.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["admin_level"], 1)
