import json
from django.test import Client


def test_optimize_route_smoke(monkeypatch):
    # Mock routing and optimization services to return deterministic data
    from fuel_optimizer.apps.route_optimizer.services.routing_service import RoutingService
    from fuel_optimizer.apps.route_optimizer.services.fuel_optimization_service import FuelOptimizationService

    class DummySummary:
        class metadata:
            distance_m = 100000.0
            duration_s = 3600.0

        sampled = []
        coords = []

    def dummy_get_route(self, start, end):
        return DummySummary()

    def dummy_optimize(self, route):
        from fuel_optimizer.apps.route_optimizer.domain.optimization_models import OptimizationResult
        res = OptimizationResult(total_cost=0, total_gallons_purchased=0, selected_stops=[], unreachable=False, notes="", candidate_count=0)
        return res

    monkeypatch.setattr(RoutingService, 'get_route', dummy_get_route)
    monkeypatch.setattr(FuelOptimizationService, 'optimize', dummy_optimize)

    client = Client()
    resp = client.post('/api/v1/optimize-route/', data=json.dumps({'start':'A','destination':'B'}), content_type='application/json')
    assert resp.status_code == 200
    data = resp.json()
    assert data['success'] is True
    assert 'route' in data
    assert 'optimization' in data
