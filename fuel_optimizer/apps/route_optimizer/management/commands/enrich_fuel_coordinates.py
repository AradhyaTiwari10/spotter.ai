from __future__ import annotations
import logging
import time
from django.core.management.base import BaseCommand
from fuel_optimizer.config.env import get_env
from fuel_optimizer.apps.route_optimizer.infrastructure.geocoding.geocoder import NominatimGeocoder, NoopGeocoder
from fuel_optimizer.apps.route_optimizer.services.geocoding_service import GeocodingService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Enrich FuelStation records with latitude/longitude using a geocoding provider. Resumable; only processes is_geocoded=False rows.'

    def add_arguments(self, parser):
        parser.add_argument('--batch', type=int, default=int(get_env('GEOCODE_BATCH', 100)), help='DB fetch batch size')
        parser.add_argument('--throttle', type=float, default=float(get_env('GEOCODE_THROTTLE', 1.0)), help='Seconds to wait between requests')
        parser.add_argument('--retries', type=int, default=int(get_env('GEOCODE_RETRIES', 3)), help='Retry attempts per request')
        parser.add_argument('--timeout', type=float, default=float(get_env('GEOCODE_TIMEOUT', 10.0)), help='Per-request timeout seconds')
        parser.add_argument('--provider', type=str, default=get_env('GEOCODER_PROVIDER', 'nominatim'), help='Geocoder provider to use')
        parser.add_argument('--limit', type=int, default=None, help='Optional limit on total stations to process')

    def handle(self, *args, **options):
        batch = options['batch']
        throttle = options['throttle']
        retries = options['retries']
        timeout = options['timeout']
        provider = options['provider']
        limit = options.get('limit')

        # choose provider
        if provider.lower() == 'nominatim':
            user_agent = get_env('NOMINATIM_USER_AGENT', 'fuel-route-optimizer')
            geocoder = NominatimGeocoder(user_agent=user_agent, default_timeout=timeout)
            logger.info('Using NominatimGeocoder with user_agent=%s', user_agent)
        else:
            geocoder = NoopGeocoder()
            logger.warning('Using NoopGeocoder; no external requests will be made')

        svc = GeocodingService(geocoder=geocoder, throttle_seconds=throttle, retries=retries, timeout=timeout)

        start = time.time()
        stats = svc.enrich(batch_size=batch, limit=limit)
        elapsed = time.time() - start

        self.stdout.write('Geocoding finished:')
        self.stdout.write(str(stats))
        self.stdout.write(f'Elapsed: {elapsed:.2f}s')
