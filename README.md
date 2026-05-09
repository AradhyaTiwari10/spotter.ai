# Fuel Route Optimizer

This project implements a Fuel Route Optimization backend in Django + DRF.

Quick start (development):

1. Create virtualenv and install:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements/base.txt

2. Set env vars (create .env from .env.example), especially ORS_API_KEY for routing.

3. Run migrations and server:
   .venv/bin/python manage.py migrate
   .venv/bin/python manage.py runserver

API:
- POST /api/v1/optimize-route/
  Body: {"start":"Dallas, TX","destination":"Phoenix, AZ"}

Response includes route summary, optimization stops, costs, and metadata with timing values.

Demo / Loom:
- Record a short Loom showing a curl or Postman call and quick code tour (RoutingService, FuelOptimizationService, API view).

Testing:
- Run tests: pytest

Notes:
- One external routing call (ORS) per request.
- Enrichment command: python manage.py enrich_fuel_coordinates --provider nominatim --batch 100 --throttle 1.0 --limit 500
