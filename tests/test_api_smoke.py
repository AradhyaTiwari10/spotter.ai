import json
import pytest
from django.test import Client
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
def test_optimize_route_smoke():
    """Smoke test for optimize-route endpoint with mocked services."""
    from fuel_optimizer.apps.route_optimizer.domain.optimization_models import OptimizationResult

    class DummySummary:
        class metadata:
            distance_m = 100000.0
            duration_s = 3600.0

        sampled = []
        coords = []

    def dummy_get_route(self, start, end):
        """Mock get_route method."""
        return DummySummary()

    def dummy_optimize(self, route):
        """Mock optimize method."""
        return OptimizationResult(
            total_cost=0,
            total_gallons_purchased=0,
            selected_stops=[],
            unreachable=False,
            notes="",
            candidate_count=0
        )

    with patch('fuel_optimizer.apps.route_optimizer.api.v1.views.optimization_view.OpenRouteServiceProvider'):
        with patch('fuel_optimizer.apps.route_optimizer.services.routing_service.RoutingService.get_route', dummy_get_route):
            with patch('fuel_optimizer.apps.route_optimizer.services.fuel_optimization_service.FuelOptimizationService.optimize', dummy_optimize):
                client = Client()
                resp = client.post(
                    '/api/v1/optimize-route/',
                    data=json.dumps({'start': 'A', 'destination': 'B'}),
                    content_type='application/json'
                )
                assert resp.status_code == 200
                data = resp.json()
                assert data['success'] is True
                assert 'route' in data
                assert 'optimization' in data


