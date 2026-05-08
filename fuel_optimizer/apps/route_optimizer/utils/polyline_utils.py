from decimal import Decimal
from typing import List, Tuple, Optional
import polyline


def decode_encoded_polyline(encoded: str, precision: int = 5) -> List[Tuple[Decimal, Decimal]]:
    """Decode encoded polyline into list of (Decimal lat, Decimal lon)."""
    points = polyline.decode(encoded, precision=precision)
    return [(Decimal(str(lat)), Decimal(str(lon))) for lat, lon in points]

