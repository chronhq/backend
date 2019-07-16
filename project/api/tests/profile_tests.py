from rest_framework import status
from django.urls import reverse
from .api_tests import (APITest, authorized)

class ProfileTests(APITest):
    """
    Profile test suite
    """

    @authorized
    def test_api_can_not_update_profile(self):
        """
        Ensure Profile permissions are operational
        """

        url = reverse("profile-detail", args=[self.django_user.profile.pk])
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
        self.client.force_authenticate(user=self.django_user)
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
        self.assertEqual(response.data[0]["user"], self.django_user.pk)

    @authorized
    def test_api_can_query_profile(self):
        """
        Ensure we can query for individual Profiles
        """

        url = reverse("profile-detail", args=[self.django_user.profile.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.django_user.pk)
