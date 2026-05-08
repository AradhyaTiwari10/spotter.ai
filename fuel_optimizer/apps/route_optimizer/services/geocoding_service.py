from __future__ import annotations
from typing import Optional, Iterable, List
import time
import logging
import random
from decimal import Decimal

from fuel_optimizer.apps.route_optimizer.repositories.fuel_station_repository import FuelStationRepository
from fuel_optimizer.apps.route_optimizer.infrastructure.geocoding.geocoder import BaseGeocoder
from fuel_optimizer.apps.route_optimizer.utils.geocoding_utils import build_geocode_query, validate_coordinates

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service orchestrating batch geocoding and persistence.

    Responsibilities:
    - Iterate non-geocoded stations in batches
    - For each station, construct geocoding query via utils
    - Call geocoder provider with retry and backoff
    - Validate coordinates and persist incrementally via repository
    - Respect throttle delay between requests
    - Provide progress logs
    """

    def __init__(self, geocoder: BaseGeocoder, repository: Optional[FuelStationRepository] = None,
                 throttle_seconds: float = 1.0, retries: int = 3, timeout: float = 10.0):
        self.geocoder = geocoder
        self.repo = repository or FuelStationRepository()
        self.throttle_seconds = float(throttle_seconds)
        self.retries = int(retries)
        self.timeout = float(timeout)

    def enrich(self, batch_size: int = 100, limit: Optional[int] = None) -> dict:
        """Run enrichment over non-geocoded stations.

        Returns stats dict with processed/ok/failed counts.

        - batch_size: how many DB rows to fetch per chunk
        - limit: optional cap on total stations to process (useful for testing)
        """
        total_pending = self.repo.model.objects.filter(is_geocoded=False).count()
        logger.info('Starting geocoding enrichment: pending=%s', total_pending)

        processed = 0
        successes = 0
        failures = 0
        skipped = 0
        start_time = time.time()

        # iterate in batches (generator yields lists of dicts)
        for batch in self.repo.iter_non_geocoded_batches(batch_size=batch_size):
            for row in batch:
                if limit is not None and processed >= limit:
                    logger.info('Limit reached (%s); stopping', limit)
                    return self._stats(processed, successes, failures, skipped, start_time)

                station_id = row['id']
                query = build_geocode_query(row)

                # if query is empty, skip
                if not query:
                    logger.warning('Empty geocode query for station id=%s; skipping', station_id)
                    skipped += 1
                    processed += 1
                    continue

                attempt = 0
                last_error = None
                while attempt <= self.retries:
                    try:
                        attempt += 1
                        logger.debug('Geocoding station id=%s attempt=%s query="%s"', station_id, attempt, query)
                        result = self.geocoder.geocode_address(query, timeout=self.timeout)
                        if result is None:
                            logger.info('No result for station id=%s', station_id)
                            failures += 1
                            break

                        lat, lon = result
                        # validate
                        if validate_coordinates(lat, lon):
                            # persist incrementally
                            updated = self.repo.update_coordinates(station_id, lat, lon, True)
                            logger.info('Geocoded station id=%s -> (%s,%s) updated=%s', station_id, lat, lon, updated)
                            successes += 1
                            break
                        else:
                            logger.warning('Invalid coords for station id=%s: (%s,%s)', station_id, lat, lon)
                            failures += 1
                            break

                    except Exception as exc:
                        last_error = exc
                        # if exceeded retries, mark failure but do not crash
                        if attempt > self.retries:
                            logger.exception('Max retries reached for station id=%s', station_id)
                            failures += 1
                            break
                        backoff = (2 ** (attempt - 1)) + random.random()
                        logger.warning('Geocode attempt %s failed for id=%s; backing off %ss; error=%s', attempt, station_id, backoff, exc)
                        time.sleep(backoff)
                        continue

                processed += 1
                # throttle between calls to respect provider rate limits
                logger.debug('Throttling for %s seconds', self.throttle_seconds)
                time.sleep(self.throttle_seconds)

        return self._stats(processed, successes, failures, skipped, start_time)

    def _stats(self, processed, successes, failures, skipped, start_time):
        elapsed = time.time() - start_time
        stats = {
            'processed': processed,
            'successes': successes,
            'failures': failures,
            'skipped': skipped,
            'elapsed_seconds': round(elapsed, 2),
        }
        logger.info('Enrichment completed: %s', stats)
        return stats

PY