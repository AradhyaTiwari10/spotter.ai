from typing import Iterable, List
from django.db import transaction
from fuel_optimizer.apps.route_optimizer.models import FuelStation


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

