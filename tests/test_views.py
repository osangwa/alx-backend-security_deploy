from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class ViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_swagger_docs(self):
        response = self.client.get('/swagger/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_api_stats(self):
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)