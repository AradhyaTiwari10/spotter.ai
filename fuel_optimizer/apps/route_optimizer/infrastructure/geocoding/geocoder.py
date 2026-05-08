"""Geocoding infrastructure interfaces and placeholders.

This module prepares the codebase for future geocoding enrichment without coupling to any provider.
"""
from typing import Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BaseGeocoder:
    """Abstract geocoder interface.

    Implementations should return (latitude, longitude) as Decimal or None if not found.
    """

    def geocode_address(self, address: str, timeout: Optional[float] = None) -> Optional[Tuple[Decimal, Decimal]]:
        raise NotImplementedError


class NoopGeocoder(BaseGeocoder):
    """Placeholder geocoder that does nothing (used for testing/dev)."""

    def geocode_address(self, address: str, timeout: Optional[float] = None):
        logger.debug("NoopGeocoder called for address: %s", address)
        return None


# Nominatim provider using geopy
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    from decimal import Decimal as D
   
    class NominatimGeocoder(BaseGeocoder):
        """Nominatim geocoder implementation using geopy.

        This wrapper keeps calls single-responsibility: one call -> one location or None.
        Retry/throttling and orchestration are handled by the higher-level service.
        """

        def __init__(self, user_agent: str = 'fuel-route-optimizer', default_timeout: float = 10.0):
            self.client = Nominatim(user_agent=user_agent, timeout=default_timeout)
            self.default_timeout = default_timeout

        def geocode_address(self, address: str, timeout: Optional[float] = None) -> Optional[Tuple[Decimal, Decimal]]:
            timeout = timeout or self.default_timeout
            try:
                loc = self.client.geocode(address, exactly_one=True, timeout=timeout)
                if loc is None:
                    return None
                # geopy returns float; convert to Decimal for DB storage consistency
                return (D(str(loc.latitude)), D(str(loc.longitude)))
            except (GeocoderTimedOut, GeocoderServiceError) as exc:
                logger.warning('Nominatim geocode error for %s: %s', address, exc)
                raise
            except Exception as exc:  # pragma: no cover - unexpected
                logger.exception('Unexpected error in NominatimGeocoder for %s: %s', address, exc)
                raise
except Exception:  # pragma: no cover - geopy not installed in some environments
    # Provide a fallback Noop implementation
    class NominatimGeocoder(BaseGeocoder):
        def __init__(self, *args, **kwargs):
            logger.warning('geopy not available; NominatimGeocoder will act as Noop')

        def geocode_address(self, address: str, timeout: Optional[float] = None):
            return None

