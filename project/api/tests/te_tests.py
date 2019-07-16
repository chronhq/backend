from rest_framework import status
from django.urls import reverse
from api.models import TerritorialEntity
from .api_tests import APITest

class TETests(APITest):
    """
    Territorial Entities test suite
    """

    def test_api_can_create_te(self):
        """
        Ensure we can create TerritorialEntities
        """

        url = reverse("territorialentity-list")
        data = {
            "wikidata_id": 9,
            "label": "Test TE",
            "color": "#fff",
            "admin_level": 4,
            "inception_date": 0,
            "dissolution_date": 1,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TerritorialEntity.objects.count(), 11)
        self.assertEqual(TerritorialEntity.objects.last().admin_level, 4)

    def test_api_can_update_te(self):
        """
        Ensure we can update TerritorialEntities
        """

        url = reverse("territorialentity-detail", args=[self.european_union.pk])
        data = {
            "wikidata_id": 10,
            "label": "Update",
            "color": "#fff",
            "admin_level": 5,
            "inception_date": 0,
            "dissolution_date": 1,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["admin_level"], 5)

    def test_api_can_query_tes(self):
        """
        Ensure we can query for all TerritorialEntities
        """

        url = reverse("territorialentity-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.european_union.pk)
        self.assertEqual(response.data[3]["stv_count"], 1)

    def test_api_can_query_te(self):
        """
        Ensure we can query for individual TerritorialEntities
        """

        url = reverse("territorialentity-detail", args=[self.european_union.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["admin_level"], 1)
