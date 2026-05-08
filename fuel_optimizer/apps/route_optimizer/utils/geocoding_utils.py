"""Utilities for geocoding: query construction, normalization, and coordinate validation."""
from typing import Optional, Dict, Tuple
from decimal import Decimal, InvalidOperation
import re

HIGHWAY_PATTERN = re.compile(r'\b(i-?\d+|us-?\d+|state-?\d+|hwy-?\d+)\b', flags=re.I)


def normalize_text(s: Optional[str]) -> str:
    if not s:
        return ""
    # collapse whitespace and strip
    s = " ".join(s.split()).strip()
    return s


def build_geocode_query(record: Dict) -> str:
    """Build a prioritized geocoding query from a station record.

    Prefer: 'Truckstop Name, City, State'
    Fallback to address when name is unhelpful.
    """
    name = normalize_text(record.get('truckstop_name') or record.get('truckstopname') or '')
    city = normalize_text(record.get('city') or '')
    state = normalize_text(record.get('state') or '')
    address = normalize_text(record.get('address') or '')

    # If name looks like a highway marker (I-44, EXIT etc), prefer address
    name_looks_like_highway = bool(HIGHWAY_PATTERN.search(name))

    if name and not name_looks_like_highway:
        parts = [p for p in (name, city, state) if p]
    elif address:
        parts = [p for p in (address, city, state) if p]
    else:
        parts = [p for p in (name, address, city, state) if p]

    # join with commas for Nominatim
    query = ', '.join(parts)
    return query


def validate_coordinates(lat: Optional[Decimal], lon: Optional[Decimal]) -> bool:
    """Validate coordinate ranges and sanity for USA.

    Latitude must be between -90 and 90. Longitude between -180 and 180.
    Additionally, apply loose USA bounds to reject obvious non-USA results.
    """
    try:
        if lat is None or lon is None:
            return False
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError, InvalidOperation):
        return False

    if not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0):
        return False

    # Loose USA bounding box: lat between 18 and 72, lon between -170 and -50
    if not (18.0 <= lat_f <= 72.0 and -170.0 <= lon_f <= -50.0):
        return False

    return True

