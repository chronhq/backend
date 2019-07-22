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
from django.test import tag
from api.models import Narrative
from .api_tests import APITest, authorized


class NarrativeTests(APITest):
    """
    Narrative test suite
    """

    @authorized
    def test_api_can_create_narrative(self):
        """
        Ensure we can create Narratives
        """

        url = reverse("narrative-list")
        data = {
            "author": "Test Author 2",
            "title": "Test Narrative",
            "url": "test2",
            "description": "This is a test narrative for automated testing.",
            "tags": ["test", "tags"],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Narrative.objects.count(), 2)
        self.assertEqual(Narrative.objects.last().author, "Test Author 2")

    @authorized
    def test_api_can_update_narrative(self):
        """
        Ensure we can update Narratives
        """

        url = reverse("narrative-detail", args=[self.norman_conquest.pk])
        data = {
            "author": "Other Test Author",
            "title": "Test Narrative",
            "url": "test2",
            "description": "This is a test narrative for automated testing.",
            "tags": ["test", "tags"],
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["author"], "Other Test Author")

    @authorized
    def test_api_can_query_narratives(self):
        """
        Ensure we can query for all Narratives
        """

        url = reverse("narrative-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["author"], "Test Author")

    @authorized
    def test_api_can_query_narrative(self):
        """
        Ensure we can query for individual Narratives
        """

        url = reverse("narrative-detail", args=[self.norman_conquest.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["author"], "Test Author")

    @tag("new")
    @authorized
    def test_api_can_query_narrative_votes(self):
        """
        Ensure upvotes and downvotes are being returned correctly
        """

        url = reverse("narrative-detail", args=[self.norman_conquest.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["votes"], {"upvotes": 1, "downvotes": 0})
