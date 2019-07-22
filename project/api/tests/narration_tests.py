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
from api.models import Narration
from .api_tests import APITest, authorized


class NarrationTests(APITest):
    """
    Narration test suite
    """

    @authorized
    def test_api_can_create_narration(self):
        """
        Ensure we can create Narrations
        """

        url = reverse("narration-list")
        data = {
            "narrative": self.norman_conquest.pk,
            "title": "Test Narration",
            "description": "This is a narration point",
            "date_label": "test",
            "map_datetime": self.JD_0002,
            "settings": self.norman_conquest_settings.pk,
            "attached_events_ids": [self.hastings.pk],
            "location": "POINT (0 0)",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Narration.objects.count(), 2)
        self.assertEqual(Narration.objects.last().title, "Test Narration")

    @authorized
    def test_api_can_update_narration(self):
        """
        Ensure we can update Narrations
        """

        url = reverse("narration-detail", args=[self.hastings_narration.pk])
        data = {
            "narrative": self.norman_conquest.pk,
            "title": "Test Narration 2",
            "description": "This is a narration point",
            "date_label": "test",
            "map_datetime": self.JD_0002,
            "settings": self.norman_conquest_settings.pk,
            "attached_events_ids": [self.hastings.pk],
            "location": "POINT (0 0)",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Narration 2")

    @authorized
    def test_api_can_query_narrations(self):
        """
        Ensure we can query for all Narrations
        """

        url = reverse("narration-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Test Narration")

    @authorized
    def test_api_can_query_narration(self):
        """
        Ensure we can query for individual Narrations
        """

        url = reverse("narration-detail", args=[self.hastings_narration.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Narration")
