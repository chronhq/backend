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
from api.models import City
from .api_tests import APITest, authorized


class CityTests(APITest):
    """
    City test suite
    """

    @authorized
    def test_api_can_create_city(self):
        """
        Ensure we can create Cities
        """

        url = reverse("city-list")
        data = {
            "wikidata_id": 2,
            "label": "London",
            "location": "POINT (10 10)",
            "inception_date": self.JD_0001,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), 2)
        self.assertEqual(City.objects.last().label, "London")

    @authorized
    def test_api_can_update_city(self):
        """
        Ensure we can update Cities
        """

        url = reverse("city-detail", args=[self.paris.pk])
        data = {
            "wikidata_id": 2,
            "label": "London",
            "location": "POINT (10 10)",
            "inception_date": self.JD_0001,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], "London")

    @authorized
    def test_api_can_query_cities(self):
        """
        Ensure we can query for all Cities
        """

        url = reverse("city-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["label"], "Paris")

    @authorized
    def test_api_can_query_city(self):
        """
        Ensure we can query for individual Cities
        """

        url = reverse("city-detail", args=[self.paris.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["label"], "Paris")
