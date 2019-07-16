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
from api.models import PoliticalRelation
from .api_tests import APITest, authorized


class PRTests(APITest):
    """
    Poltical Relations test suite
    """

    @authorized
    def test_api_can_create_pr(self):
        """
        Ensure we can create PoliticalRelations
        """

        url = reverse("politicalrelation-list")
        data = {
            "start_date": self.JD_0001,
            "end_date": self.JD_0002,
            "parent": self.european_union.pk,
            "child": self.france.pk,
            "control_type": PoliticalRelation.GROUP,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PoliticalRelation.objects.count(), 2)
        self.assertEqual(
            PoliticalRelation.objects.last().control_type, PoliticalRelation.GROUP
        )

    @authorized
    def test_api_can_update_pr(self):
        """
        Ensure we can update PoliticalRelations
        """

        url = reverse("politicalrelation-detail", args=[self.EU_germany.pk])
        data = {
            "start_date": self.JD_0001,
            "end_date": self.JD_0002,
            "parent": self.european_union.pk,
            "child": self.france.pk,
            "control_type": PoliticalRelation.GROUP,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["control_type"], PoliticalRelation.GROUP)

    @authorized
    def test_api_can_query_prs(self):
        """
        Ensure we can query for all PoliticalRelations
        """

        url = reverse("politicalrelation-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["control_type"], PoliticalRelation.INDIRECT)

    @authorized
    def test_api_can_query_pr(self):
        """
        Ensure we can query for individual PoliticalRelations
        """

        url = reverse("politicalrelation-detail", args=[self.EU_germany.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["control_type"], PoliticalRelation.INDIRECT)
