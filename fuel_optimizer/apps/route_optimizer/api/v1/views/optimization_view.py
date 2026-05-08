import time
import logging
from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers.request_serializers import OptimizeRouteRequestSerializer
from ..serializers.response_serializers import OptimizeRouteResponseSerializer
from fuel_optimizer.apps.route_optimizer.infrastructure.routing.ors_provider import OpenRouteServiceProvider
from fuel_optimizer.apps.route_optimizer.services.routing_service import RoutingService
from fuel_optimizer.apps.route_optimizer.services.fuel_optimization_service import FuelOptimizationService

logger = logging.getLogger(__name__)

class OptimizeRouteView(APIView):
    """Public endpoint to optimize a route between two locations.

    Thin controller: validation -> orchestration -> serialization
    """

    def post(self, request):
        req_ser = OptimizeRouteRequestSerializer(data=request.data)
        if not req_ser.is_valid():
            return Response({'success': False, 'errors': req_ser.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = req_ser.validated_data
        start = data['start']
        destination = data['destination']

        logger.info('OptimizeRoute request start=%s destination=%s', start, destination)

        # Orchestration with timing
        total_start = time.time()
        routing_start = time.time()
        try:
            provider = OpenRouteServiceProvider()
            routing = RoutingService(provider)
            # RoutingService expects tuples for coordinates or strings handled by provider
            route_summary = routing.get_route(start, destination)
        except Exception as exc:
            logger.exception('Routing failure')
            return Response({'success': False, 'message': 'Routing provider error'}, status=status.HTTP_502_BAD_GATEWAY)
        routing_end = time.time()

        optimization_start = time.time()
        try:
            optimizer = FuelOptimizationService()
            # internal candidate builder is used inside optimize
            result = optimizer.optimize(route_summary)
        except Exception:
            logger.exception('Optimization failure')
            return Response({'success': False, 'message': 'Optimization failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        optimization_end = time.time()
        total_end = time.time()

        # assemble response DTO
        route_dto = {
            'distance_miles': float(route_summary.metadata.distance_m / 1609.344),
            'duration_hours': float(route_summary.metadata.duration_s / 3600.0),
            'sampled_points': [[float(c.lat), float(c.lon)] for c in route_summary.sampled]
        }

        stops = []
        for s in result.selected_stops:
            stops.append({
                'station_id': s.station_id,
                'name': s.name,
                'lat': float(s.lat),
                'lon': float(s.lon),
                'price_per_gallon': Decimal(s.price_per_gallon).quantize(Decimal('0.001')) if hasattr(s,'price_per_gallon') else Decimal('0'),
                'distance_from_start_miles': s.distance_from_start_miles,
                'gallons_purchased': s.gallons_purchased,
                'cost': s.cost,
            })

        optimization_dto = {
            'total_cost': result.total_cost,
            'total_gallons': result.total_gallons_purchased,
            'stops': stops,
        }

        metadata = {
            'candidate_stations': len(result.selected_stops) + 0,  # placeholder; repository could provide candidate count
            'selected_stops': len(result.selected_stops),
            'optimization_runtime_ms': (optimization_end - optimization_start) * 1000.0,
            'routing_runtime_ms': (routing_end - routing_start) * 1000.0,
            'total_runtime_ms': (total_end - total_start) * 1000.0,
        }

        resp = {
            'success': True,
            'route': route_dto,
            'optimization': optimization_dto,
            'metadata': metadata,
            'message': ''
        }

        # validate response through serializer (ensures contract)
        resp_ser = OptimizeRouteResponseSerializer(data=resp)
        if not resp_ser.is_valid():
            logger.error('Response validation failed: %s', resp_ser.errors)
            return Response({'success': False, 'message': 'Internal serialization error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info('OptimizeRoute completed routing_ms=%.1f opt_ms=%.1f total_ms=%.1f candidates=%d selected=%d',
                    metadata['routing_runtime_ms'], metadata['optimization_runtime_ms'], metadata['total_runtime_ms'],
                    metadata['candidate_stations'], metadata['selected_stops'])

        return Response(resp_ser.validated_data, status=status.HTTP_200_OK)
