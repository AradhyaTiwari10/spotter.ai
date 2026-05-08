from __future__ import annotations
from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import List, Dict, Tuple, Optional
import time
import math
import logging

from fuel_optimizer.apps.route_optimizer.repositories.fuel_station_repository import FuelStationRepository
from fuel_optimizer.apps.route_optimizer.domain.optimization_models import FuelStop, OptimizationResult
from fuel_optimizer.apps.route_optimizer.utils.distance import haversine_meters, meters_to_miles
from fuel_optimizer.apps.route_optimizer.domain.routing_models import RouteCoordinate, RouteSummary

logger = logging.getLogger(__name__)

# Financial precision and quantization
getcontext().prec = 9
CENTS = Decimal('0.01')
PRICE_Q = Decimal('0.001')  # price precision aligned with stored retail_price
GALLON_Q = Decimal('0.0001')

# Vehicle assumptions
MPG = Decimal('10')
MAX_RANGE_MILES = Decimal('500')
TANK_CAPACITY_GALLONS = (MAX_RANGE_MILES / MPG).quantize(GALLON_Q)

DEFAULT_CORRIDOR_RADIUS_MILES = 10.0  # increased default for better candidate coverage in sparse datasets

class FuelOptimizationService:
    """Service that finds candidate stations along a sampled route and runs a greedy optimization to minimize fuel cost.

    Input: RouteSummary (from routing service)
    Output: OptimizationResult with selected stops and cost breakdown
    """

    def __init__(self, repository: Optional[FuelStationRepository] = None, corridor_radius_miles: float = DEFAULT_CORRIDOR_RADIUS_MILES):
        self.repo = repository or FuelStationRepository()
        self.corridor_radius_miles = float(corridor_radius_miles)

    def _degrees_delta(self, lat: float, miles: float) -> Tuple[float, float]:
        """Return approximate lat/lon degree deltas for a given miles radius at latitude lat."""
        # 1 degree latitude ~ 69 miles
        lat_delta = miles / 69.0
        # longitude degrees vary by latitude
        lon_degree_miles = 69.0 * math.cos(math.radians(lat))
        if lon_degree_miles <= 0:
            lon_delta = miles / 69.0
        else:
            lon_delta = miles / lon_degree_miles
        return lat_delta, lon_delta

    def _compute_sample_cumulative_miles(self, sampled: List[RouteCoordinate]) -> List[Decimal]:
        """Compute cumulative distance along sampled route points in miles."""
        cum = []
        total = 0.0
        prev = None
        for p in sampled:
            if prev is None:
                cum.append(Decimal('0'))
                prev = p
                continue
            d = haversine_meters(float(prev.lat), float(prev.lon), float(p.lat), float(p.lon))
            total += d
            cum.append(Decimal(str(meters_to_miles(total))))
            prev = p
        return cum

    def _build_candidates(self, sampled: List[RouteCoordinate]) -> List[Dict]:
        """Find stations within corridor radius of sampled points and return deduped candidates sorted by route order."""
        candidates: Dict[str, Dict] = {}
        sample_cum_miles = self._compute_sample_cumulative_miles(sampled)
        logger.info('Building candidates from %d sampled points; corridor=%.2f miles', len(sampled), self.corridor_radius_miles)

        for idx, p in enumerate(sampled):
            lat = float(p.lat)
            lon = float(p.lon)
            lat_delta, lon_delta = self._degrees_delta(lat, self.corridor_radius_miles)
            min_lat, max_lat = lat - lat_delta, lat + lat_delta
            min_lon, max_lon = lon - lon_delta, lon + lon_delta

            qs = self.repo.find_stations_in_bbox(min_lat, max_lat, min_lon, max_lon)
            count = 0
            for row in qs:
                count += 1
                # compute exact distance from sample to station
                st_lat = float(row['latitude'])
                st_lon = float(row['longitude'])
                dist_m = haversine_meters(lat, lon, st_lat, st_lon)
                dist_miles = Decimal(str(meters_to_miles(dist_m)))
                if float(dist_miles) <= self.corridor_radius_miles:
                    key = row['opis_truckstop_id'] or f"id-{row['id']}"
                    # preserve earliest occurrence (lowest idx)
                    existing = candidates.get(key)
                    # cumulative miles to sample point
                    sample_mile = sample_cum_miles[idx] if idx < len(sample_cum_miles) else Decimal('0')
                    station_mile = (sample_mile + dist_miles).quantize(Decimal('0.0001'))
                    price = Decimal(str(row['retail_price'])).quantize(PRICE_Q)
                    if existing is None or (existing and station_mile < existing['distance_from_start_miles']):
                        candidates[key] = {
                            'station_id': row['id'],
                            'opis_truckstop_id': row['opis_truckstop_id'],
                            'name': row['truckstop_name'],
                            'lat': Decimal(str(row['latitude'])),
                            'lon': Decimal(str(row['longitude'])),
                            'price': price,
                            'distance_from_start_miles': station_mile,
                            'sample_index': idx,
                            'sample_distance_miles': sample_mile,
                            'distance_to_sample_miles': dist_miles,
                        }
            logger.debug('Sample idx=%d found %d bbox candidates', idx, count)

        # sort candidates by distance_from_start_miles
        candidate_list = list(candidates.values())
        candidate_list.sort(key=lambda x: (x['distance_from_start_miles'], x['price']))
        logger.info('Total candidates discovered: %d', len(candidate_list))
        return candidate_list

    def optimize(self, route_summary: RouteSummary, start_fuel_gallons: Optional[Decimal] = None) -> OptimizationResult:
        """Main orchestration: generate candidates and run greedy optimization.

        start_fuel_gallons defaults to full tank.
        """
        start_time = time.time()
        if start_fuel_gallons is None:
            start_fuel_gallons = TANK_CAPACITY_GALLONS
        start_fuel_gallons = start_fuel_gallons.quantize(GALLON_Q)

        sampled = route_summary.sampled
        if not sampled:
            raise ValueError('No sampled route points provided')

        candidates = self._build_candidates(sampled)
        logger.info('Candidate count: %d', len(candidates))

        # prepare sorted distances and route length
        route_length_miles = Decimal(str(round(route_summary.metadata.distance_m / 1609.344, 6)))

        # Convert candidate distances to Decimal
        for c in candidates:
            c['distance_from_start_miles'] = Decimal(c['distance_from_start_miles']).quantize(Decimal('0.0001'))

        # Greedy optimization
        decisions: List[FuelStop] = []
        total_cost = Decimal('0')
        total_gallons = Decimal('0')
        current_pos = Decimal('0')
        remaining_gallons = start_fuel_gallons
        mp_g = MPG
        tank_cap = TANK_CAPACITY_GALLONS

        idx = 0
        n = len(candidates)

        unreachable = False
        notes = ''

        while True:
            # check if destination reachable
            remaining_range_miles = (remaining_gallons * mp_g).quantize(Decimal('0.0001'))
            if current_pos + remaining_range_miles >= route_length_miles:
                logger.info('Destination within current range: current_pos=%.3f remaining_range=%.3f route_length=%.3f', float(current_pos), float(remaining_range_miles), float(route_length_miles))
                break

            # find candidates ahead within reach
            reachable_limit = (current_pos + remaining_range_miles)
            reachable = [c for c in candidates if c['distance_from_start_miles'] > current_pos and c['distance_from_start_miles'] <= reachable_limit]

            if not reachable:
                # cannot reach any station nor destination
                logger.error('No reachable stations from current_pos=%.3f with remaining_range=%.3f', float(current_pos), float(remaining_range_miles))
                unreachable = True
                notes = 'No reachable stations; route cannot be completed with current fuel constraints'
                break

            # choose cheapest reachable station
            reachable.sort(key=lambda x: (x['price'], x['distance_from_start_miles']))
            next_station = reachable[0]

            # travel to next_station
            distance_to_next = (next_station['distance_from_start_miles'] - current_pos)
            gallons_consumed = (Decimal(str(distance_to_next)) / mp_g).quantize(GALLON_Q)
            remaining_gallons -= gallons_consumed
            if remaining_gallons < Decimal('0'):
                logger.error('Consumed more fuel than available while reaching next station')
                unreachable = True
                notes = 'Consumed more fuel than available'
                break

            # At next station, decide purchase amount
            # Find cheaper station ahead within full tank from this station
            station_pos = next_station['distance_from_start_miles']
            full_reach = station_pos + (tank_cap * mp_g)
            future_within_full = [c for c in candidates if c['distance_from_start_miles'] > station_pos and c['distance_from_start_miles'] <= full_reach]
            cheaper_ahead = [c for c in future_within_full if c['price'] < next_station['price']]

            if cheaper_ahead:
                # pick the nearest cheaper ahead
                cheaper_ahead.sort(key=lambda x: x['distance_from_start_miles'])
                target = cheaper_ahead[0]
                dist_to_target = (target['distance_from_start_miles'] - station_pos)
                gallons_needed = (Decimal(str(dist_to_target)) / mp_g).quantize(GALLON_Q)
                # ensure enough to reach target (consider current remaining)
                purchase_gallons = max(Decimal('0'), gallons_needed - remaining_gallons)
                reason = f'Cheaper ahead at {float(target["distance_from_start_miles"]):.2f} mi; buy enough to reach'
            else:
                # no cheaper ahead within full reach; fill to full
                purchase_gallons = (tank_cap - remaining_gallons).quantize(GALLON_Q)
                reason = 'No cheaper ahead within full tank; fill to full'

            # cap purchase to non-negative
            if purchase_gallons < Decimal('0'):
                purchase_gallons = Decimal('0')

            # compute cost
            price = next_station['price']
            cost = (purchase_gallons * price).quantize(CENTS, rounding=ROUND_HALF_UP)
            total_cost += cost
            total_gallons += purchase_gallons
            remaining_gallons += purchase_gallons

            # record decision
            stop = FuelStop(
                station_id=next_station['station_id'],
                opis_truckstop_id=next_station['opis_truckstop_id'],
                name=next_station['name'],
                lat=next_station['lat'],
                lon=next_station['lon'],
                price_per_gallon=price,
                distance_from_start_miles=next_station['distance_from_start_miles'],
                gallons_purchased=purchase_gallons,
                cost=cost,
                remaining_range_miles=(remaining_gallons * mp_g).quantize(Decimal('0.0001'))
            )
            logger.info('Selected stop at %.2f mi price=%s purchase=%.4f gal cost=%s reason=%s', float(stop.distance_from_start_miles), str(price), float(stop.gallons_purchased), str(cost), reason)

            decisions.append(stop)

            # advance current position to station
            current_pos = station_pos

            # remove candidate stations behind or at current_pos to avoid revisiting
            candidates = [c for c in candidates if c['distance_from_start_miles'] > current_pos]

        elapsed = time.time() - start_time
        logger.info('Optimization completed in %.2fs total_cost=%s stops=%d unreachable=%s', elapsed, str(total_cost), len(decisions), unreachable)

        result = OptimizationResult(
            total_cost=total_cost.quantize(CENTS, rounding=ROUND_HALF_UP),
            total_gallons_purchased=total_gallons.quantize(GALLON_Q),
            selected_stops=decisions,
            unreachable=unreachable,
            notes=notes,
        )
        return result
