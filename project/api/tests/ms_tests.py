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
from api.models import MapSettings
from .api_tests import APITest, authorized


class MSTests(APITest):
    """
    Map Settings test suite
    """

    @authorized
    def test_api_can_create_ms(self):
        """
        Ensure we can create MapSettings
        """

        url = reverse("mapsettings-list")
        data = {"zoom_min": 1, "zoom_max": 13}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MapSettings.objects.count(), 2)
        self.assertEqual(MapSettings.objects.last().zoom_min, 1.0)

    @authorized
    def test_api_can_update_ms(self):
        """
        Ensure we can update MapSettings
        """

        url = reverse("mapsettings-detail", args=[self.norman_conquest_settings.pk])
        data = {"zoom_min": 5, "zoom_max": 13}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["zoom_min"], 5)

    @authorized
    def test_api_can_query_mss(self):
        """
        Ensure we can query for all MapSettings
        """

        url = reverse("mapsettings-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["zoom_min"], 1)

    @authorized
    def test_api_can_query_ms(self):
        """
        Ensure we can query for individual MapSettings
        """

        url = reverse("mapsettings-detail", args=[self.norman_conquest_settings.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["zoom_min"], 1)
