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
from api.models import NarrativeVote
from .api_tests import APITest, authorized


class NarrativeVoteTests(APITest):
    """
    Narrative Vote test suite
    """

    @authorized
    def test_api_can_create_narrativevote(self):
        """
        Ensure we can vote on Narratives
        """

        url = reverse("narrativevote-list")
        data = {"narrative": self.norman_conquest.pk, "vote": 0}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        objects = NarrativeVote.objects.filter(user_id=self.django_user.pk)
        self.assertEqual(objects.count(), 1)
        self.assertEqual(objects.last().vote, 0)

    @authorized
    def test_api_can_update_narrativevote(self):
        """
        Ensure we can change our NarrativeVotes
        """

        url = reverse("narrativevote-list")
        data = {"narrative": self.norman_conquest.pk, "vote": 1}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            NarrativeVote.objects.filter(user_id=self.django_user.pk).count(), 1
        )
        self.assertEqual(
            NarrativeVote.objects.filter(user_id=self.django_user.pk).last().vote, 1
        )

    @authorized
    def test_api_can_query_narrativevotes(self):
        """
        Ensure we can query for all NarrativeVotes
        """

        url = reverse("narrativevote-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["vote"], True)

    @authorized
    def test_api_can_query_narrativevote(self):
        """
        Ensure we can query for individual NarrativeVotes
        """

        url = reverse("narrativevote-detail", args=[self.norman_conquest_vote.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["vote"], True)

    @authorized
    def test_api_can_remove_narrativevote(self):
        """
        Ensure we can remove our NarrativeVote
        """

        url = reverse("narrativevote-list")
        data = {"narrative": self.norman_conquest.pk, "vote": None}
        response = self.client.post(url, data, format="json")
        self.assertEqual(
            NarrativeVote.objects.filter(user_id=self.django_user.pk).count(), 0
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
