import json
from django.test import Client
from django.test.testcases import TestCase


class HealthEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_endpoint_returns_200(self):
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'fuel-route-optimizer')


class OptimizeRouteEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_optimize_route_missing_fields(self):
        response = self.client.post(
            '/api/v1/optimize-route/',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success', True))

    def test_optimize_route_invalid_json(self):
        response = self.client.post(
            '/api/v1/optimize-route/',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
