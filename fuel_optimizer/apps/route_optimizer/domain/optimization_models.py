from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class FuelStop:
    station_id: int
    opis_truckstop_id: str
    name: str
    lat: Optional[Decimal]
    lon: Optional[Decimal]
    price_per_gallon: Decimal
    distance_from_start_miles: Decimal
    gallons_purchased: Decimal
    cost: Decimal
    remaining_range_miles: Decimal

@dataclass
class RouteSegmentDecision:
    from_mile: Decimal
    to_mile: Decimal
    consumed_gallons: Decimal

@dataclass
class OptimizationResult:
    total_cost: Decimal
    total_gallons_purchased: Decimal
    selected_stops: list[FuelStop]
    unreachable: bool
    notes: str
    candidate_count: int = 0
