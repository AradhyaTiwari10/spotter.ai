from typing import Tuple, Optional, List, Dict, Any
from decimal import Decimal

class BaseRoutingProvider:
    """Abstract routing provider interface.

    Implementations must provide get_route which returns a dict with at least:
    - distance_m: total distance in meters
    - duration_s: estimated duration in seconds
    - coords: list of (Decimal lat, Decimal lon) tuples representing the route geometry
    - encoded_polyline: optional encoded polyline string (provider format)
    - raw: optional raw provider response
    """

    def get_route(self, start: Tuple[Decimal, Decimal], end: Tuple[Decimal, Decimal], profile: str = 'driving-car', timeout: Optional[float] = None) -> Dict[str, Any]:
        raise NotImplementedError
