import logging
from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional

from .base import BaseRoutingProvider

logger = logging.getLogger(__name__)

# Try to import httpx and polyline; provide fallbacks if not available
try:
    import httpx
    import polyline
    from fuel_optimizer.config.env import get_env
    HTTPX_AVAILABLE = True
except Exception:
    HTTPX_AVAILABLE = False


class OpenRouteServiceProvider(BaseRoutingProvider):
    """OpenRouteService provider using httpx.

    Note: Caller must provide ORS_API_KEY via environment (ORS_API_KEY) or pass api_key param.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 10.0):
        if not HTTPX_AVAILABLE:
            raise RuntimeError('httpx and/or polyline required for OpenRouteServiceProvider')
        self.api_key = api_key
        if self.api_key is None:
            # lazy import of env loader
            from fuel_optimizer.config.env import get_env
            self.api_key = get_env('ORS_API_KEY')
        if not self.api_key:
            raise RuntimeError('ORS_API_KEY not configured')

        self.base_url = base_url or 'https://api.openrouteservice.org'
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout)

    def get_route(self, start: Tuple[Decimal, Decimal], end: Tuple[Decimal, Decimal], profile: str = 'driving-car', timeout: Optional[float] = None) -> Dict[str, Any]:
        timeout = timeout or self.timeout
        url = f"{self.base_url}/v2/directions/{profile}"
        # If textual locations provided, attempt lightweight geocoding via geopy.Nominatim
        def _ensure_coords(p):
            # Accept Decimal tuple (lat, lon) or string address
            if isinstance(p, str):
                # perform geocoding
                try:
                    from geopy.geocoders import Nominatim
                    geoloc = Nominatim(user_agent='fuel-route-optimizer').geocode(p, exactly_one=True, timeout=10)
                    if not geoloc:
                        raise ValueError(f'Geocoding failed for {p}')
                    lat = float(geoloc.latitude)
                    lon = float(geoloc.longitude)
                    return (lon, lat)
                except Exception as exc:
                    logger.exception('Geocoding inside ORS provider failed: %s', exc)
                    raise
            else:
                # assume tuple (Decimal lat, Decimal lon)
                return (float(p[1]), float(p[0]))

        coords = [_ensure_coords(start), _ensure_coords(end)]
        payload = {
            'coordinates': coords,
            'instructions': False,
            'geometry': True,
            'geometry_simplify': False,
        }
        headers = {
            'Authorization': str(self.api_key),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            response = self.client.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.exception('ORS request failed: %s', exc)
            raise

        # Parse response: support geojson "features" and ORS v2 "routes"
        coords_list: List[Tuple[Decimal, Decimal]] = []
        encoded_polyline: Optional[str] = None
        distance_m = None
        duration_s = None

        if 'features' in data and data.get('features'):
            feat = data['features'][0]
            geom = feat.get('geometry', {})
            if geom.get('type') == 'LineString' and isinstance(geom.get('coordinates'), list):
                for lon, lat in geom['coordinates']:
                    coords_list.append((Decimal(str(lat)), Decimal(str(lon))))
            props = feat.get('properties', {})
            summary = props.get('summary', {})
            distance_m = summary.get('distance')
            duration_s = summary.get('duration')
        elif 'routes' in data and data.get('routes'):
            r = data['routes'][0]
            # geometry may be encoded polyline or geojson-like
            geometry = r.get('geometry')
            if isinstance(geometry, str):
                # encoded polyline
                encoded_polyline = geometry
                decoded = polyline.decode(geometry)
                for lat, lon in decoded:
                    coords_list.append((Decimal(str(lat)), Decimal(str(lon))))
            elif isinstance(geometry, dict) and geometry.get('type') == 'LineString':
                for lon, lat in geometry.get('coordinates', []):
                    coords_list.append((Decimal(str(lat)), Decimal(str(lon))))
            # distance/duration
            summary = r.get('summary') or {}
            distance_m = summary.get('distance') or (r.get('segments') or [{}])[0].get('distance')
            duration_s = summary.get('duration') or (r.get('segments') or [{}])[0].get('duration')
        else:
            raise ValueError('Unexpected ORS response format')

        return {
            'distance_m': float(distance_m) if distance_m is not None else None,
            'duration_s': float(duration_s) if duration_s is not None else None,
            'coords': coords_list,
            'encoded_polyline': encoded_polyline,
            'raw': data,
        }


class NoopRoutingProvider(BaseRoutingProvider):
    """A simple provider that returns a linear interpolation between start and end for testing."""

    def get_route(self, start: Tuple[Decimal, Decimal], end: Tuple[Decimal, Decimal], profile: str = 'driving-car', timeout: Optional[float] = None) -> Dict[str, Any]:
        # create a simple straight-line route with 10 segments
        from fuel_optimizer.apps.route_optimizer.utils.distance import haversine_meters
        num = 10
        lat1, lon1 = float(start[0]), float(start[1])
        lat2, lon2 = float(end[0]), float(end[1])
        coords: List[Tuple[Decimal, Decimal]] = []
        total_m = 0.0
        last = None
        for i in range(num + 1):
            t = i / num
            lat = lat1 + (lat2 - lat1) * t
            lon = lon1 + (lon2 - lon1) * t
            coords.append((Decimal(str(lat)), Decimal(str(lon))))
            if last is not None:
                total_m += haversine_meters(last[0], last[1], lat, lon)
            last = (lat, lon)
        # approximate duration assuming 60 mph -> 26.8224 m/s
        duration_s = total_m / 26.8224 if total_m else 0
        return {
            'distance_m': total_m,
            'duration_s': duration_s,
            'coords': coords,
            'encoded_polyline': None,
            'raw': None,
        }
