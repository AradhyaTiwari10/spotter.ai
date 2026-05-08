from math import radians, sin, cos, sqrt, atan2
from typing import Tuple

EARTH_RADIUS_M = 6371000.0


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two lat/lon points using Haversine."""
    lat1_r = radians(lat1)
    lat2_r = radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(lat1_r) * cos(lat2_r) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_M * c


def meters_to_miles(meters: float) -> float:
    return meters / 1609.344


def validate_lat_lon(lat: float, lon: float) -> bool:
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except Exception:
        return False
    return -90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0
