from __future__ import annotations
from decimal import Decimal
from typing import Tuple, List
import logging

from fuel_optimizer.apps.route_optimizer.infrastructure.routing.base import BaseRoutingProvider
from fuel_optimizer.apps.route_optimizer.domain.routing_models import RouteCoordinate, RouteSummary, RouteMetadata
from fuel_optimizer.apps.route_optimizer.utils.sampling import sample_route_coords
from fuel_optimizer.apps.route_optimizer.utils.distance import meters_to_miles, validate_lat_lon

logger = logging.getLogger(__name__)


class RoutingService:
    """Service responsible for retrieving a route from a provider and preparing geometry for downstream processing."""

    def __init__(self, provider: BaseRoutingProvider, sample_miles: float = 25.0):
        self.provider = provider
        self.sample_meters = float(sample_miles) * 1609.344

    def get_route(self, start: Tuple[float, float], end: Tuple[float, float]) -> RouteSummary:
        """Retrieve route from provider (single external call) and prepare decoded geometry and sampled points."""
        logger.info('Requesting route from provider: start=%s end=%s', start, end)
        # Convert to Decimal pairs expected by provider
        start_d = (Decimal(str(start[0])), Decimal(str(start[1])))
        end_d = (Decimal(str(end[0])), Decimal(str(end[1])))

        data = self.provider.get_route(start_d, end_d)

        coords_raw = data.get('coords') or []
        if not coords_raw:
            logger.error('Provider returned empty geometry')
            raise RuntimeError('Empty route geometry')

        # validate coords
        valid_coords = []
        for lat, lon in coords_raw:
            if validate_lat_lon(float(lat), float(lon)):
                valid_coords.append(RouteCoordinate(lat=Decimal(str(lat)), lon=Decimal(str(lon))))
            else:
                logger.warning('Invalid coordinate from provider: (%s,%s)', lat, lon)

        if not valid_coords:
            raise RuntimeError('No valid coordinates in route')

        # sample geometry
        # convert coords to tuples for sampler
        coord_tuples = [(c.lat, c.lon) for c in valid_coords]
        sampled_tuples = sample_route_coords(coord_tuples, self.sample_meters)
        sampled = [RouteCoordinate(lat=Decimal(str(pt[0])), lon=Decimal(str(pt[1]))) for pt in sampled_tuples]

        metadata = RouteMetadata(
            distance_m=float(data.get('distance_m') or 0.0),
            duration_s=float(data.get('duration_s') or 0.0),
            point_count=len(valid_coords)
        )

        summary = RouteSummary(coords=valid_coords, encoded_polyline=data.get('encoded_polyline'), sampled=sampled, metadata=metadata)
        logger.info('Route prepared: distance_m=%.1f duration_s=%.1f points=%d sampled=%d', metadata.distance_m, metadata.duration_s, metadata.point_count, len(sampled))
        return summary
