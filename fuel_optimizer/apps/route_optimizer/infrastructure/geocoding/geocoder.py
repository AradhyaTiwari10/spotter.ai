"""Geocoding infrastructure interfaces and placeholders.

This module prepares the codebase for future geocoding enrichment without coupling to any provider.
"""
from typing import Optional, Tuple
from decimal import Decimal


class BaseGeocoder:
    """Abstract geocoder interface.

    Implementations should return (latitude, longitude) as Decimal or None if not found.
    """

    def geocode_address(self, address: str) -> Optional[Tuple[Decimal, Decimal]]:
        raise NotImplementedError


class NoopGeocoder(BaseGeocoder):
    """Placeholder geocoder that does nothing (used for testing/dev)."""

    def geocode_address(self, address: str):
        return None

