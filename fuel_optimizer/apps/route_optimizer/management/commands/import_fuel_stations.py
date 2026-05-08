"""Management command to ingest fuel station CSVs into FuelStation model.

Usage:
    python manage.py import_fuel_stations --path path/to/file.csv --batch 1000

The command performs:
 - streaming CSV read (low memory)
 - normalization and validation
 - USA filtering (filters out specific Canadian provinces)
 - deterministic deduplication
 - bulk inserts using repository.bulk_create_stations
"""
from __future__ import annotations
import csv
from pathlib import Path
from decimal import InvalidOperation
from django.core.management.base import BaseCommand
from fuel_optimizer.config.env import BASE_DIR
from fuel_optimizer.apps.route_optimizer.utils.data_normalization import (
    clean_str,
    normalize_state,
    is_canadian_province,
    parse_decimal,
)
from fuel_optimizer.apps.route_optimizer.repositories.fuel_station_repository import FuelStationRepository
from fuel_optimizer.apps.route_optimizer.models import FuelStation


class Command(BaseCommand):
    help = 'Import fuel stations from a CSV into the FuelStation table.'

    def add_arguments(self, parser):
        parser.add_argument('--path', '-p', type=str, default=str(BASE_DIR / 'datasets' / 'fuel_prices' / 'fuel-prices-for-be-assessment.csv'))
        parser.add_argument('--batch', type=int, default=1000, help='Bulk insert batch size')

    def handle(self, *args, **options):
        path = Path(options['path'])
        batch_size = int(options['batch'])

        if not path.exists():
            self.stderr.write(f"CSV file not found: {path}")
            return

        repo = FuelStationRepository()

        total_rows = 0
        inserted = 0
        duplicates_skipped = 0
        non_usa_skipped = 0
        invalid_rows = 0

        seen_keys: set = set()
        buffer: list[FuelStation] = []

        # Helper to resolve CSV columns robustly
        def find_value(row: dict, candidates: list[str]) -> str:
            for k, v in row.items():
                key = k.strip().lower().replace(' ', '').replace('_', '')
                if key in candidates:
                    return v
            return ''

        # canonical candidates
        keys_map = {
            'opis': ['opistruckstopid', 'opistruckstopid', 'opisid', 'opistruckstopid'],
            'truckstop_name': ['truckstopname', 'truckstop_name', 'stationname', 'name'],
            'address': ['address', 'addr'],
            'city': ['city'],
            'state': ['state', 'province', 'region'],
            'rack_id': ['rackid', 'rack_id'],
            'retail_price': ['retailprice', 'retail_price', 'price', 'retail'],
        }

        with path.open(newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                total_rows += 1
                try:
                    opis_raw = find_value(row, keys_map['opis'])
                    truckstop_raw = find_value(row, keys_map['truckstop_name'])
                    address_raw = find_value(row, keys_map['address'])
                    city_raw = find_value(row, keys_map['city'])
                    state_raw = find_value(row, keys_map['state'])
                    rack_raw = find_value(row, keys_map['rack_id'])
                    price_raw = find_value(row, keys_map['retail_price'])

                    opis = clean_str(opis_raw)
                    truckstop_name = clean_str(truckstop_raw)
                    address = clean_str(address_raw)
                    city = clean_str(city_raw)
                    state = normalize_state(state_raw)
                    rack_id = clean_str(rack_raw)

                    # Filter out Canadian provinces
                    if is_canadian_province(state):
                        non_usa_skipped += 1
                        continue

                    # Deterministic deduplication key
                    dedup_key = (opis, truckstop_name, address, city, state)
                    if dedup_key in seen_keys:
                        duplicates_skipped += 1
                        continue
                    seen_keys.add(dedup_key)

                    # Parse price into Decimal with required precision
                    retail_price = parse_decimal(price_raw)

                    obj = FuelStation(
                        opis_truckstop_id=opis,
                        truckstop_name=truckstop_name,
                        address=address,
                        city=city,
                        state=state,
                        rack_id=rack_id or None,
                        retail_price=retail_price,
                    )
                    buffer.append(obj)

                    if len(buffer) >= batch_size:
                        created = repo.bulk_create_stations(buffer, batch_size=batch_size)
                        inserted += created
                        buffer = []

                except InvalidOperation:
                    invalid_rows += 1
                except Exception as exc:  # pragma: no cover - defensive
                    self.stderr.write(f"Unexpected error processing row {total_rows}: {exc}")
                    invalid_rows += 1

        # flush remainder
        if buffer:
            created = repo.bulk_create_stations(buffer, batch_size=batch_size)
            inserted += created

        self.stdout.write(f"Total rows: {total_rows}")
        self.stdout.write(f"Inserted: {inserted}")
        self.stdout.write(f"Duplicates skipped: {duplicates_skipped}")
        self.stdout.write(f"Non-USA skipped: {non_usa_skipped}")
        self.stdout.write(f"Invalid rows: {invalid_rows}")

