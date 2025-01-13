from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class GetNodesViewTests(APITestCase):
    def test_get_nodes(self):
        """
        Ensure the /nodes endpoint returns a list of nodes and the total count.
        """
        url = reverse("metagraph")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("nodes", response.data)
        self.assertIn("total", response.data)
        self.assertIsInstance(response.data["nodes"], list)
        self.assertIsInstance(response.data["total"], int)
