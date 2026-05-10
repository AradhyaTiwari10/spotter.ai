# Fuel Route Optimizer

A production-grade Django backend API for optimizing fuel routes across the USA. Given a start and destination (text addresses or city names), it:

1. Geocodes both locations to GPS coordinates
2. Calls the OpenRouteService API **once** to get the full route
3. Runs a custom optimization algorithm to find the most cost-effective fuel stops
4. Returns the route, selected fuel stations, and total cost estimate

**Key Features:**
- ⚡ Fast responses (<2 seconds typical)
- 💰 Fuel cost optimization with real station prices
- 🚗 Respects 500-mile vehicle range (multiple fuel stops when needed)
- 🔧 Clean architecture (views → services → repositories → models)
- ✅ 5+ passing tests, CI/CD with GitHub Actions

---

## Quick Start (Local Development)

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/AradhyaTiwari10/spotter.ai.git
cd spotter.ai

# Create virtualenv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt
```

### 2. Configure API Key

Get a free OpenRouteService API key:
1. Visit https://openrouteservice.org/
2. Sign up and generate an API key
3. Set environment variable:

```bash
export ORS_API_KEY="your_key_here"
```

### 3. Run Django Setup

```bash
# Create database and run migrations
python manage.py migrate --noinput

# Load sample fuel station data (optional)
python manage.py import_fuel_stations
```

### 4. Start Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Server runs at: `http://127.0.0.1:8000`

---

## API Usage

### Endpoint: POST `/api/v1/optimize-route/`

**Request:**
```json
{
  "start": "Dallas, TX",
  "destination": "Phoenix, AZ"
}
```

**Response:**
```json
{
  "success": true,
  "route": {
    "distance_m": 1234567,
    "duration_s": 18000,
    "waypoints": [...],
    "geometry": "..."
  },
  "optimization": {
    "total_cost": 247.50,
    "total_gallons_purchased": 20.5,
    "selected_stops": [
      {
        "id": 42,
        "name": "Shell Station",
        "coordinates": [33.123, -97.456],
        "gallons_to_purchase": 10.5,
        "distance_from_start_m": 250000
      },
      ...
    ],
    "candidate_count": 47
  }
}
```

---

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fuel_optimizer

# Run specific test file
pytest tests/test_api_smoke.py -v
```

All tests use mocked services—no external API calls during testing.

---

## Project Structure

```
fuel_optimizer/
├── apps/route_optimizer/
│   ├── api/v1/
│   │   ├── views/
│   │   │   └── optimization_view.py      # Main API endpoint
│   │   └── serializers/
│   │       ├── request_serializers.py
│   │       └── response_serializers.py
│   ├── services/
│   │   ├── routing_service.py            # Orchestrates route fetching
│   │   ├── fuel_optimization_service.py  # Cost optimization algorithm
│   │   └── geocoding_service.py          # Address → coordinates
│   ├── infrastructure/
│   │   └── routing/
│   │       ├── base.py                   # Provider interface
│   │       └── ors_provider.py           # OpenRouteService integration
│   ├── domain/
│   │   ├── optimization_models.py        # Data models
│   │   └── routing_models.py
│   └── repositories/
│       └── fuel_station_repository.py    # Database queries
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   └── urls.py
tests/
├── test_api_smoke.py                     # Integration tests
├── test_api_integration.py
└── conftest.py                           # Pytest configuration
```

---

## Recording Your Demo (Loom)

See [LOOM_SCRIPT.md](LOOM_SCRIPT.md) for a detailed second-by-second script including:
- Setup instructions
- Exact narration for each segment
- Timing breakdown (5 min total)
- Tips for professional recording

**Quick checklist before recording:**
- [ ] Django server running: `python manage.py runserver 0.0.0.0:8000`
- [ ] Postman opened with collection ready
- [ ] ORS_API_KEY configured (or use mock in tests)
- [ ] VS Code ready to show code
- [ ] Practice narration once silently

---

## Deployment

### Environment Variables (Production)

```bash
ORS_API_KEY=your_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host/db
```

### Run with Docker

```bash
docker build -t fuel-optimizer .
docker run -e ORS_API_KEY=your_key -p 8000:8000 fuel-optimizer
```

See [Dockerfile](Dockerfile) and [docker-compose.yml](docker-compose.yml).

---

## Tech Stack

- **Framework:** Django 5.2 (latest stable)
- **API:** Django REST Framework
- **Routing:** OpenRouteService (free tier)
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Testing:** pytest, pytest-django
- **CI/CD:** GitHub Actions
- **HTTP Client:** httpx (async-capable)

---

## Performance Notes

- **Single external API call:** Route fetching happens once, then cached in memory
- **Response time:** Typically <2 seconds (depends on external routing API)
- **Algorithm:** Greedy optimization (efficient for this use case)
- **Database:** Fuel stations pre-indexed for quick lookups

---

## Requirements Met

✅ **Build the app in latest stable Django** — Django 5.2  
✅ **Results returned quickly** — <2 seconds typical  
✅ **Minimal external API calls** — 1 call to ORS  
✅ **Includes Postman demo** — See [postman_collection.json](postman_collection.json)  
✅ **Code shared on GitHub** — Public repo with clean commit history  
✅ **5-min code overview** — Script in [LOOM_SCRIPT.md](LOOM_SCRIPT.md)

---

## License

Private project for assessment.

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
