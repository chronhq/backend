from rest_framework import status
from django.urls import reverse
from api.models import MapSettings
from .api_tests import APITest

class MSTests(APITest):
    """
    Map Settings test suite
    """

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

    def test_api_can_update_ms(self):
        """
        Ensure we can update MapSettings
        """

        url = reverse("mapsettings-detail", args=[self.norman_conquest_settings.pk])
        data = {"zoom_min": 5, "zoom_max": 13}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["zoom_min"], 5)

    def test_api_can_query_mss(self):
        """
        Ensure we can query for all MapSettings
        """

        url = reverse("mapsettings-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["zoom_min"], 1)

    def test_api_can_query_ms(self):
        """
        Ensure we can query for individual MapSettings
        """

        url = reverse("mapsettings-detail", args=[self.norman_conquest_settings.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["zoom_min"], 1)
