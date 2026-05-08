from typing import List, Tuple
from decimal import Decimal
from .distance import haversine_meters


def sample_route_coords(coords: List[Tuple[Decimal, Decimal]], interval_meters: float) -> List[Tuple[Decimal, Decimal]]:
    """Sample route coordinates approximately every interval_meters.

    Simple greedy sampler: include first point, walk segments accumulating distance, include point when threshold crossed, include last point.
    """
    if not coords:
        return []
    if len(coords) <= 2:
        return coords

    sampled = [coords[0]]
    acc = 0.0
    last_point = coords[0]

    for pt in coords[1:]:
        # convert Decimal to float for distance calc
        d = haversine_meters(float(last_point[0]), float(last_point[1]), float(pt[0]), float(pt[1]))
        acc += d
        if acc >= interval_meters:
            sampled.append(pt)
            acc = 0.0
            last_point = pt
        else:
            last_point = pt

    if sampled[-1] != coords[-1]:
        sampled.append(coords[-1])

    return sampled
