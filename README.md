# Fuel Route Optimizer

A production-grade Django backend API for optimizing fuel routes across the USA. Accepts start and destination locations, makes one external routing API call, and returns optimal fuel stops with cost estimates.

## Quick Start

### 1. Setup Environment

```bash
# Create virtualenv
python -m venv .venv
source .venv/bin/activate

# Install base dependencies
pip install -r requirements/base.txt

# For development and testing
pip install -r requirements/dev.txt
```

### 2. Configure Environment Variables

```bash
# Copy example and update with your ORS API key
cp .env.example .env
# Edit .env and set: ORS_API_KEY=your_key_here
```

Get a free ORS API key: https://openrouteservice.org/

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Start Server

```bash
python manage.py runserver
# Server runs on http://127.0.0.1:8000/
```

## API Endpoints

### Health Check
```bash
GET /api/v1/health/

Response:
{
  "status": "healthy",
  "service": "fuel-route-optimizer"
}
```

### Optimize Route
```bash
POST /api/v1/optimize-route/
Content-Type: application/json

Request:
{
  "start": "Dallas, TX",
  "destination": "Phoenix, AZ"
}

Response:
{
  "success": true,
  "route": {
    "distance_miles": 1064.08,
    "duration_hours": 16.05,
    "sampled_points": [[lat, lon], ...]
  },
  "optimization": {
    "total_cost": 456.78,
    "total_gallons_purchased": 120.5,
    "selected_stops": [
      {
        "opis_truckstop_id": "123",
        "name": "Station Name",
        "lat": 33.12,
        "lon": -97.45,
        "distance_from_start_miles": 250.5,
        "price_per_gallon": 3.89,
        "gallons_purchased": 45.2,
        "cost": 175.93,
        "remaining_range_miles": 452.0
      }
    ],
    "unreachable": false,
    "notes": ""
  },
  "metadata": {
    "candidate_stations": 42,
    "routing_ms": 1463.4,
    "optimization_ms": 39.4,
    "total_ms": 1502.8
  }
}
```

## Testing

Run all tests:
```bash
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov
```

Current test coverage:
- Smoke tests for service initialization
- Integration tests for health and optimize endpoints
- Request validation tests

## Architecture

### Clean Architecture Layers

```
api/              - HTTP layer (views, serializers)
services/         - Business logic (routing, optimization, geocoding)
repositories/     - Data access layer
domain/           - DTOs and domain models
infrastructure/   - External providers (routing, geocoding)
optimization/     - Optimization algorithms
cache/            - Caching layer (future)
tests/            - Unit and integration tests
```

### Key Services

- **RoutingService**: Makes one ORS API call, decodes geometry, samples route points
- **FuelOptimizationService**: Discovers candidate stations, runs greedy optimizer
- **GeocodingService**: Enriches station coordinates using Nominatim

## Development

### Enriching Fuel Station Coordinates

The project includes ~6,855 fuel stations from CSV. To geocode coordinates:

```bash
python manage.py enrich_fuel_coordinates \
  --provider nominatim \
  --batch 100 \
  --throttle 1.0 \
  --limit 500
```

This command:
- Uses Nominatim (free, but rate-limited)
- Processes 100 stations per batch
- Respects 1-second throttle between requests
- Can be resumed if interrupted

### Project Structure

```
fuel_optimizer/
├── apps/
│   └── route_optimizer/
│       ├── api/v1/             # HTTP endpoints
│       ├── services/           # Business logic
│       ├── repositories/       # Data access
│       ├── domain/             # DTOs
│       ├── infrastructure/     # External providers
│       ├── optimization/       # Optimizer algorithms
│       ├── models.py           # Django models
│       └── migrations/         # DB migrations
├── config/
│   ├── settings/
│   │   ├── base.py            # Shared settings
│   │   ├── local.py           # Development settings
│   │   └── production.py      # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── docker/                     # Docker config
├── requirements/               # Dependency management
├── tests/                      # Test suite
└── manage.py
```

## Performance Notes

- **One API Call**: Uses OpenRouteService for routing only (not searching for stations)
- **Local Optimization**: All station discovery and optimization happens locally
- **Route Sampling**: Route is sampled every ~40 miles for efficient corridor searches
- **Decimal Arithmetic**: Uses Python Decimal for precise financial calculations

## Vehicle Assumptions

- Max Range: 500 miles
- Fuel Efficiency: 10 MPG
- Tank Capacity: 50 gallons

## Dependencies

Core:
- Django 5.2+ - Web framework
- Django REST Framework 3.15+ - API framework
- OpenRouteService - Routing provider
- Geopy/Nominatim - Geocoding (optional, for coordinate enrichment)
- Pandas - Data processing
- Polyline - Route geometry encoding

Development:
- pytest - Testing framework
- pytest-django - Django testing integration
- pytest-cov - Code coverage

## Docker

Build and run:
```bash
docker-compose up -d

# Access API at http://localhost:8000/
```

## Troubleshooting

**ORS API Key Issues**
```
Check .env file has ORS_API_KEY set
Test with: curl http://localhost:8000/api/v1/health/
```

**Migrations not applied**
```bash
python manage.py migrate --run-syncdb
```

**Poor candidate station coverage**
- Run enrichment: `python manage.py enrich_fuel_coordinates`
- For production: Use pre-geocoded vendor data or paid geocoding service

## Notes

Response includes:
- **candidate_stations**: Number of stations found within corridor
- **routing_ms / optimization_ms**: Performance metrics
- **unreachable**: True if route cannot be completed with constraints

## Next Steps

1. Record demo (3-5 min Loom showing Postman call + code overview)
2. Expand test coverage (unit tests for services)
3. Consider PostGIS for large-scale spatial indexing
4. Add async support for background enrichment jobs
