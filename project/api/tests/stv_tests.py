from rest_framework import status
from django.urls import reverse
from api.models import SpacetimeVolume
from .api_tests import APITest

class STVTests(APITest):
    """
    SpacetimeVolume test suite
    """

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
            "territory": "POLYGON((3 3, 3 4, 4 4, 3 3))",
            "visual_center": "POINT(1.2 1.8)",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SpacetimeVolume.objects.count(), 2)
        self.assertEqual(SpacetimeVolume.objects.last().references, ["ref"])

    def test_api_can_update_stv(self):
        """
        Ensure we can update SpacetimeVolumes
        """

        url = reverse("spacetimevolume-detail", args=[self.alsace_stv.pk])
        data = {
            "start_date": self.JD_0001,
            "end_date": self.JD_0005,
            "entity": self.france.pk,
            "references": ["ref"],
            "territory": "POLYGON((1 1, 1 2, 2 2, 1 1))",
            "visual_center": "POINT (0.7 0.7)",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["end_date"], str(self.JD_0005))

    def test_api_can_query_stv(self):
        """
        Ensure we can query for individual SpacetimeVolumes
        """

        url = reverse("spacetimevolume-detail", args=[self.alsace_stv.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["end_date"], str(self.JD_0002))
