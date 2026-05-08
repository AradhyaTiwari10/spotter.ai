"""Data normalization and validation utilities for station ingestion.

Functions are deliberately small and pure to allow unit testing and reuse.
"""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional

CANADIAN_PROVINCES = {"AB", "BC", "MB", "NB", "NS", "ON", "QC", "SK", "YT"}


def clean_str(value: Optional[str]) -> str:
    """Trim whitespace and normalize internal spacing. Returns empty string for falsy values."""
    if value is None:
        return ""
    return " ".join(value.split()).strip()


def normalize_state(value: Optional[str]) -> str:
    """Normalize state/province codes to uppercase short form where possible."""
    s = clean_str(value)
    return s.upper()


def is_canadian_province(value: Optional[str]) -> bool:
    """Return True if the provided state/province code is a Canadian province to be filtered out."""
    return normalize_state(value) in CANADIAN_PROVINCES


def parse_decimal(value: Optional[str]) -> Decimal:
    """Parse a numeric string into Decimal with 3 decimal places precision.

    Raises InvalidOperation on failure.
    """
    if value is None:
        raise InvalidOperation("No value")
    s = clean_str(value)
    if s.startswith("$"):
        s = s[1:]
    # Remove commas commonly found in CSV numbers
    s = s.replace(",", "")
    d = Decimal(s)
    return d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

