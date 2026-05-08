from typing import Iterable, List, Dict, Generator
from django.db import transaction
from fuel_optimizer.apps.route_optimizer.models import FuelStation
from decimal import Decimal


class FuelStationRepository:
    """Repository abstraction for FuelStation persistence and queries.

    Keeps ORM access centralized to avoid scattering ORM calls across business logic.
    """

    def __init__(self, model=FuelStation):
        self.model = model

    def bulk_create_stations(self, station_objs: Iterable[FuelStation], batch_size: int = 1000) -> int:
        """Efficiently bulk-insert model instances.

        Returns the number of created objects (best-effort).
        """
        station_list = list(station_objs)
        if not station_list:
            return 0
        created = self.model.objects.bulk_create(station_list, batch_size=batch_size)
        try:
            return len(created) if created is not None else len(station_list)
        except TypeError:
            return len(station_list)

    def get_by_state(self, state: str):
        return self.model.objects.filter(state=state).order_by('retail_price')

    def get_by_city(self, city: str):
        return self.model.objects.filter(city__iexact=city).order_by('retail_price')

    def get_all_geocoded(self):
        return self.model.objects.filter(is_geocoded=True)

    def get_non_geocoded(self):
        return self.model.objects.filter(is_geocoded=False)

    def count_stations(self) -> int:
        return self.model.objects.count()

    def iter_non_geocoded_batches(self, batch_size: int = 1000) -> Generator[List[Dict], None, None]:
        """Yield lists of non-geocoded station rows as dicts to avoid loading all objects into memory.

        Each dict contains minimal fields required for geocoding: id, opis_truckstop_id, truckstop_name, address, city, state
        """
        qs = self.model.objects.filter(is_geocoded=False).values('id', 'opis_truckstop_id', 'truckstop_name', 'address', 'city', 'state')
        batch: List[Dict] = []
        for row in qs.iterator():
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    def update_coordinates(self, station_id: int, latitude: Decimal, longitude: Decimal, is_geocoded: bool = True) -> int:
        """Update coordinates for a station by id. Returns number of rows updated."""
        return self.model.objects.filter(pk=station_id).update(latitude=latitude, longitude=longitude, is_geocoded=is_geocoded)

    def find_stations_in_bbox(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float):
        """Return iterator of station dicts inside the provided lat/lon bounding box.

        Values returned include id, opis_truckstop_id, truckstop_name, address, city, state, latitude, longitude, retail_price
        """
        qs = self.model.objects.filter(latitude__isnull=False, longitude__isnull=False,
                                       latitude__gte=min_lat, latitude__lte=max_lat,
                                       longitude__gte=min_lon, longitude__lte=max_lon)
        return qs.values('id', 'opis_truckstop_id', 'truckstop_name', 'address', 'city', 'state', 'latitude', 'longitude', 'retail_price')

