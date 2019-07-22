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
from api.models import CachedData
from .api_tests import APITest, authorized
from .test_data import wiki_cd


class CDTests(APITest):
    """
    Cached Data test suite
    """

    @authorized
    @wiki_cd
    def test_api_can_create_cd(self):
        """
        Ensure we can create CachedData
        """

        url = reverse("cacheddata-list")
        data = {
            "wikidata_id": 2,
            "location": "Point(0 1)",
            "date": self.JD_0001,
            "event_type": CachedData.DOCUMENT,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CachedData.objects.count(), 2)
        self.assertEqual(CachedData.objects.last().event_type, CachedData.DOCUMENT)

    @authorized
    @wiki_cd
    def test_api_can_create_cd_othertype(self):
        """
        Ensure we can create CachedData with an event_type not in the choices
        """

        url = reverse("cacheddata-list")
        data = {
            "wikidata_id": 2,
            "location": "Point(0 1)",
            "date": self.JD_0001,
            "event_type": 555,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CachedData.objects.count(), 2)
        self.assertEqual(CachedData.objects.last().event_type, 555)

    @authorized
    @wiki_cd
    def test_api_can_update_cd(self):
        """
        Ensure we can update CachedData
        """

        url = reverse("cacheddata-detail", args=[self.hastings.pk])
        data = {
            "wikidata_id": 1,
            "location": "Point(0 0)",
            "date": self.JD_0001,
            "event_type": CachedData.DOCUMENT,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["event_type"], CachedData.DOCUMENT)

    @authorized
    @wiki_cd
    def test_api_can_query_cds(self):
        """
        Ensure we can query for all CachedDatas
        """

        url = reverse("cacheddata-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["event_type"], CachedData.BATTLE)

    @authorized
    @wiki_cd
    def test_api_can_query_cd(self):
        """
        Ensure we can query for individual CachedDatas
        """

        url = reverse("cacheddata-detail", args=[self.hastings.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["event_type"], CachedData.BATTLE)
