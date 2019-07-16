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
        self.assertEqual(NarrativeVote.objects.count(), 1)
        self.assertEqual(NarrativeVote.objects.last().vote, 0)

    @authorized
    def test_api_can_update_narrativevote(self):
        """
        Ensure we can change our NarrativeVotes
        """

        url = reverse("narrativevote-list")
        data = {"narrative": self.norman_conquest.pk, "vote": 1}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NarrativeVote.objects.count(), 1)
        self.assertEqual(NarrativeVote.objects.last().vote, 1)

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
        self.assertEqual(NarrativeVote.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
