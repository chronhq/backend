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

import json
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.gis.geos import GEOSGeometry
from django.urls import reverse
from django.test import override_settings
from api.models import SpacetimeVolume
from api.views.stv_view import _calculate_area
from .api_tests import APITest, authorized


class STVTests(APITest):
    """
    SpacetimeVolume test suite
    """

    def test_stv_area_is_correct(self):
        """ Check Area computations """
        self.assertEqual(
            _calculate_area(GEOSGeometry("POLYGON(EMPTY)", srid=4326)), 0.0
        )
        area = _calculate_area(
            GEOSGeometry("SRID=4326;POLYGON((-1 -1,-1 1,1 1, 1 -1, -1 -1))")
        )
        self.assertEqual(area, 49238887518.5544)

    @override_settings(CACHEOPS_ENABLED=False)
    @authorized
    def test_api_can_create_stv(self):
        """
        Ensure we can create SpacetimeVolumes
        """

        url = reverse("spacetimevolume-list")
        data = {
            "start_date": self.JD_0001,
            "end_date": self.JD_0002,
            "entity": self.germany.pk,
            "references": ["ref"],
            "territory": SimpleUploadedFile(
                "polygon.plain", b"SRID=4326;POLYGON((3 3, 3 4, 4 4, 3 3))"
            ),
            "visual_center": "SRID=4326;POINT(1.2 1.8)",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SpacetimeVolume.objects.count(), 2)
        self.assertEqual(SpacetimeVolume.objects.last().references, ["ref"])

    @override_settings(CACHEOPS_ENABLED=False)
    @authorized
    def test_api_can_update_stv(self):
        """
        Ensure we can update SpacetimeVolumes
        """

        url = reverse("spacetimevolume-detail", args=[self.alsace_stv.pk])
        data = {
            "start_date": self.JD_0001,
            "end_date": self.JD_0005,
            "entity": self.france.pk,
            "references": ["ref", "fer"],
            # "territory": SimpleUploadedFile(
            #     "polygon.plain", b"SRID=4326;POLYGON((1 1, 1 2, 2 2, 1 1))"
            # ),
            "visual_center": "SRID=4326;POINT(0.7 0.7)",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["end_date"], str(self.JD_0005))
        self.assertEqual(response.data["references"], ["ref", "fer"])

    @override_settings(CACHEOPS_ENABLED=False)
    @authorized
    def test_api_can_query_stv(self):
        """
        Ensure we can query for individual SpacetimeVolumes
        """

        url = reverse("spacetimevolume-detail", args=[self.alsace_stv.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["end_date"], str(self.JD_0002))

    @override_settings(CACHEOPS_ENABLED=False)
    @authorized
    def test_api_can_not_create_stv(self):
        """
        Ensure territory checks for overlapping STVs are working
        """

        url = reverse("spacetimevolume-list")
        data = {
            "start_date": self.JD_0001,
            "end_date": self.JD_0002,
            "entity": self.germany.pk,
            "references": ["ref"],
            "territory": SimpleUploadedFile(
                "polygon.json",
                json.dumps(
                    {
                        "type": "Polygon",
                        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
                        "coordinates": [
                            [
                                [-27.421875, -14.264383087562637],
                                [-4.5703125, -15.623036831528252],
                                [-2.4609375, 28.92163128242129],
                                [-27.421875, 29.22889003019423],
                                [-27.421875, -14.264383087562637],
                            ]
                        ],
                    }
                ).encode(),
                content_type="application/json",
            ),
            "visual_center": "SRID=4326;POINT(1.2 1.8)",
        }
        data_overlapping = {
            "start_date": self.JD_0001,
            "end_date": self.JD_0002,
            "entity": self.italy.pk,
            "references": ["ref"],
            "territory": SimpleUploadedFile(
                "polygon.json",
                json.dumps(
                    {
                        "type": "Polygon",
                        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
                        "coordinates": [
                            [
                                [-39.7265625, 30.14512718337613],
                                [-50.2734375, -16.97274101999901],
                                [22.148437499999996, -12.211180191503997],
                                [34.80468749999999, 22.917922936146045],
                                [-39.7265625, 30.14512718337613],
                            ]
                        ],
                    }
                ).encode(),
                content_type="application/json",
            ),
            "visual_center": "SRID=4326;POINT(1.2 1.8)",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data_overlapping)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
