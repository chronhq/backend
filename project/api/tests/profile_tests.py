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
from .api_tests import APITest, authorized


class ProfileTests(APITest):
    """
    Profile test suite
    """

    def setUp(self):
        self.client.force_authenticate(user=self.django_user)
        super().setUp()

    @authorized
    def test_api_can_not_update_profile(self):
        """
        Ensure Profile permissions are operational
        """

        url = reverse("profile-detail", args=[self.test_user.profile.pk])
        data = {"location": "POINT (10 10)"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @authorized
    def test_api_can_update_profile(self):
        """
        Ensure user's own Profile can be updated
        """

        url = reverse("profile-detail", args=[self.django_user.profile.pk])
        data = {"location": "POINT (10 10)"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["location"]["coordinates"], [10.0, 10.0])

    @authorized
    def test_api_can_query_profiles(self):
        """
        Ensure we can query for all Profiles
        """

        url = reverse("profile-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        valid = list(filter(lambda x: x["user"] == self.django_user.pk, response.data))
        self.assertTrue(len(valid) == 1)

    @authorized
    def test_api_can_query_profile(self):
        """
        Ensure we can query for individual Profiles
        """

        url = reverse("profile-detail", args=[self.django_user.profile.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.django_user.pk)
