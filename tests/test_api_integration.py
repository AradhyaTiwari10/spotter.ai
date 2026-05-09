import json
from django.test import Client
from django.test.testcases import TestCase


class HealthEndpointTest(TestCase):
    """Test health check endpoint."""

    def setUp(self):
        self.client = Client()

    def test_health_endpoint_returns_200(self):
        """Test that health endpoint returns 200 status code."""
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'fuel-route-optimizer')


class OptimizeRouteEndpointTest(TestCase):
    """Test optimize-route endpoint validation."""

    def setUp(self):
        self.client = Client()

    def test_optimize_route_missing_fields(self):
        """Test endpoint with missing required fields."""
        response = self.client.post(
            '/api/v1/optimize-route/',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success', True))

    def test_optimize_route_invalid_json(self):
        """Test endpoint with invalid JSON."""
        response = self.client.post(
            '/api/v1/optimize-route/',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_optimize_route_invalid_method(self):
        """Test endpoint with GET instead of POST."""
        response = self.client.get('/api/v1/optimize-route/')
        self.assertIn(response.status_code, [404, 405])  # Not Found or Method Not Allowed

