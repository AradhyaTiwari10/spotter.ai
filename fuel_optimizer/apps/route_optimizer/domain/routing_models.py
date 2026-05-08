from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

@dataclass
class RouteCoordinate:
    lat: Decimal
    lon: Decimal

@dataclass
class RouteMetadata:
    distance_m: float
    duration_s: float
    point_count: int

@dataclass
class RouteSummary:
    coords: List[RouteCoordinate]
    encoded_polyline: Optional[str]
    sampled: List[RouteCoordinate]
    metadata: RouteMetadata
