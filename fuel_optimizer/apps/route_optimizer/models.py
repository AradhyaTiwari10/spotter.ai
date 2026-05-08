from __future__ import annotations
from django.db import models
from decimal import Decimal
from django.utils import timezone


class FuelStation(models.Model):
    """Database model representing a fuel station.

    Design notes:
    - retail_price uses DecimalField for financial precision (max_digits=6, decimal_places=3).
    - latitude/longitude are nullable to allow future geocoding enrichment.
    - indexes added for common query fields to support performant lookups.
    """

    opis_truckstop_id = models.CharField(max_length=64, db_index=True)
    truckstop_name = models.CharField(max_length=255)
    address = models.CharField(max_length=512)
    city = models.CharField(max_length=128, db_index=True)
    state = models.CharField(max_length=16, db_index=True)
    rack_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    retail_price = models.DecimalField(max_digits=6, decimal_places=3, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_geocoded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fuel Station'
        verbose_name_plural = 'Fuel Stations'
        indexes = [
            models.Index(fields=['state'], name='fuelstation_state_idx'),
            models.Index(fields=['retail_price'], name='fuelstation_price_idx'),
            models.Index(fields=['city'], name='fuelstation_city_idx'),
            models.Index(fields=['opis_truckstop_id'], name='fuelstation_opis_idx'),
            models.Index(fields=['rack_id'], name='fuelstation_rack_idx'),
        ]

    def __str__(self) -> str:
        return f"{self.truckstop_name} ({self.city}, {self.state})"

