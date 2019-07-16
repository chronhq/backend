from rest_framework import status
from django.urls import reverse
from api.models import City
from .api_tests import (APITest, authorized)

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
