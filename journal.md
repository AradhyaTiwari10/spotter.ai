# Milestone 1 - Project Foundation

## Objective
Initialize project foundation and clean architecture skeleton for Fuel Route Optimization API.

## Architecture Decisions
- Django + DRF for robust API capabilities.
- Clean, domain-oriented app under fuel_optimizer/apps/route_optimizer.
- Split settings (base/local/production) for environment-specific config.

## Folder Structure Decisions
- apps/ contains domain app with well-separated layers: api, services, repositories, domain, infrastructure, etc.

## Dependencies Added
- django, djangorestframework, django-cors-headers, python-dotenv, requests, httpx, pandas, geopy, polyline

## Environment Configuration
- dotenv based env.py for reading .env
- .env.example provided

## Docker Configuration
- Dockerfile using python:3.11-slim optimized for layer caching
- docker-compose.yml for local development

## API Initialization
- Versioned API at /api/v1/
- Health endpoint implemented at /api/v1/health/

## Files Added
- project skeleton, settings split, Docker files, requirements

## Files Modified
- None (fresh project)

## Performance Considerations
- Prepared for async/httpx, caching, PostGIS integration.
- Minimal middleware and JSON renderer by default for performance.

## Technical Debt
- No DB configuration beyond sqlite; production DB and secrets management pending.

## Next Steps
- Implement route optimization service, caching layers, and database models.

## Git Commit
feat(setup): initialize clean architecture django backend

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

# Milestone 1 Finalization

## Validation Completed
- Ensured folder structure matches Clean Architecture layout.
- Added missing __init__.py files to make packages importable.
- Created dataset folder and sample CSV for future ETL.

## Dataset Infrastructure Added
- datasets/fuel_prices/fuel-prices-for-be-assessment.csv added (sample placeholder).
- datasets/README.md documents dataset handling rules and ETL expectations.

## Architecture Review
- Folder separation (api, services, repositories, domain, infrastructure, cache) enables clear separation of concerns.
- Services layer will house use-cases; repositories will abstract persistence allowing easy swap to PostGIS or other DBs.
- Optimization engines will be placed under optimization/ and be pluggable via defined interfaces in domain/.
- Caching layer will be integrated under cache/ and invoked from services/infrastructure where needed.

## Performance Review
- Minimal middleware stack to reduce overhead.
- DRF configured to use JSONRenderer only to reduce renderer negotiation overhead.
- Dependencies kept minimal; heavy libs (pandas, geopy, polyline) included for future  consider moving heavy processing to async workers.processing 
- Docker image uses python:slim and removes build deps to reduce image size; further multi-stage builds can improve size.

## Docker Validation
- Dockerfile and docker-compose.yml prepared for local dev with volume mounts.
- Image layering optimized by installing requirements before copying source; consider pinning requirements.txt for reproducible builds.

## Django Validation
- Settings split into base/local/production and dotenv loader present.
- URL routing configured to include app API urls under /api/v1/.
- Health endpoint implemented at /api/v1/health/ returning expected JSON.
- Note: Full runtime validation requires installing dependencies and running migrations locally or in container.

## Cleanup Performed
- Added missing __init__.py files.
- Created datasets README and placeholder CSV.
- .gitignore already present to prevent committing env and large files.

## Remaining Technical Debt
- Production DB configuration and secrets management.
- Pinning dependency versions for reproducible CI builds.
- CI pipeline and tests scaffolding.
- Add schema files and sample data for datasets.

## Readiness For Milestone 2
- Project structure is ready for implementing route optimizer service, repositories and caching layers.

## Final Git Commit
chore(setup): finalize milestone 1 architecture and dataset infrastructure

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

# Milestone 2 - Data Engineering and Persistence Layer

## Objective
Implement data ingestion, persistence and repository abstractions for fuel station data to prepare for geospatial enrichment and optimized route calculations.

## Dataset Analysis
- Dataset contains ~8151 rows (~7531 valid US rows) with retail_price floats and no coordinates.
- Dataset includes Canadian provinces (AB, BC, MB, NB, NS, ON, QC, SK, YT) which are filtered out.

## Database Model Decisions
- Created FuelStation model with nullable latitude/longitude and is_geocoded flag.
- Retail price stored as DecimalField(max_digits=6, decimal_places=3) for financial precision.
- No destructive uniqueness constraints; deduplication performed during ingestion.

## Decimal Precision Strategy
- Prices parsed into Decimal and quantized to 3 decimal places (0.001) using ROUND_HALF_UP.

## Deduplication Strategy
- Deterministic key used: (opis_truckstop_id, truckstop_name, address, city, state).
- Duplicates are skipped during ingestion; no DB uniqueness constraint to avoid accidental rejection of near-duplicates.

## USA Filtering Logic
- Rows with province/state codes matching known Canadian provinces are filtered out before persistence.

## Repository Layer Decisions
- Implemented FuelStationRepository to centralize ORM access (bulk_create, queries, counts).
- Keeps business logic decoupled from ORM and eases PostGIS migration in repositories later.

## Import Pipeline Architecture
- management/commands/import_fuel_stations.py performs streaming CSV read, normalization, USA filtering, deterministic deduplication, and bulk inserts.
- Uses low-memory streaming, configurable batch size, and reports ingestion statistics.

## Geocoding Preparation
- infrastructure/geocoding/ contains BaseGeocoder and NoopGeocoder placeholders for future enrichment workflows and a planned enrich_fuel_coordinates command.

## Database Indexing Decisions
- Indexed fields: state, retail_price, city, opis_truckstop_id, rack_id to support common lookups and sorting.

## Performance Considerations
- bulk_create used to minimize DB round-trips.
- Streaming CSV read to reduce memory footprint.
- Deduplication performed in-memory using a set of deterministic keys (acceptable given dataset size). For much larger datasets, move deduplication to DB-level strategies or use external keys/hashes.

## Files Added
- fuel_optimizer/apps/route_optimizer/models.py
- fuel_optimizer/apps/route_optimizer/repositories/fuel_station_repository.py
- fuel_optimizer/apps/route_optimizer/utils/data_normalization.py
- fuel_optimizer/apps/route_optimizer/management/commands/import_fuel_stations.py
- fuel_optimizer/apps/route_optimizer/infrastructure/geocoding/geocoder.py
- fuel_optimizer/apps/route_optimizer/migrations/0001_initial.py
- fuel_optimizer/apps/route_optimizer/admin.py

## Files Modified
- journal.md (appended)

## Validation Results
- Migration file created (0001_initial.py). Run `python manage.py migrate` to apply.
- Import command prepared; run locally to ingest dataset and view statistics.

## Technical Debt
- For very large datasets: deduplication may need to move to DB or use streaming hash-based de-duplication to limit memory.
- No automated tests included yet; add pytest and CI in next steps.
- Pin dependencies for reproducible builds.

## Next Steps
- Implement enrich_fuel_coordinates command to batch geocode non-geocoded stations.
- Add unit tests for normalization utilities and repository methods.
- Add PostGIS-backed repository implementations and spatial indexes.

## Git Commit
feat(data): implement fuel station ingestion and persistence layer

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>

# Debugging and Fixes

## App Registration Fix
- Issue: Explicit app config path not used in INSTALLED_APPS; migrations not discovered by Django.
- Fix: Updated fuel_optimizer/config/settings/base.py to use full app config path:
  'fuel_optimizer.apps.route_optimizer.apps.RouteOptimizerConfig'
- Result: Migration discovery and application now work correctly.

## Migration Generation
- Initial migration (0001_initial.py) was manually created in Milestone 2 but not auto-discovered by Django.
- Ran `python manage.py makemigrations route_optimizer` to generate and properly register migration.
- Validated with `python manage.py showmigrations route_optimizer`.
- Applied successfully: Applying route_optimizer.0001_initial... OK

## Ingestion Validation
- After migrations applied, re-ran ingestion command.
- Results: 6855 fuel stations imported from 8151 total rows.
  - Duplicates skipped: 676 (due to deterministic deduplication)
  - Non-USA rows skipped: 620 (Canadian provinces)
  - Invalid rows: 0
- Sample verified: WOODSHED OF BIG CABIN (Big Cabin, OK) - $3.007
- Decimal precision confirmed: prices stored as Decimal(max_digits=6, decimal_places=3).

## Technical Notes
- Django app discovery requires explicit AppConfig path in INSTALLED_APPS.
- Auto-generated migration replaces manual 0001_initial.py (Git will handle cleanup on next commit).


# Milestone 3 - Geocoding and Spatial Enrichment Infrastructure

## Objective
Implement offline geocoding enrichment infrastructure to populate coordinates for FuelStation records reliably, resumably, and responsibly.

## Geocoding Architecture Decisions
- Introduced a GeocodingService that orchestrates batch enrichment and isolates retry/throttle logic from provider implementations.
- Provider implementations live under infrastructure/geocoding/ and conform to BaseGeocoder interface.

## Provider Abstraction Strategy
- BaseGeocoder defines geocode_address(address, timeout) -> Optional[(lat, lon)].
- NominatimGeocoder implemented using geopy.Nominatim.
- NoopGeocoder exists for offline/dev safety and testing.

## Retry Logic Strategy
- Exponential backoff with jitter for transient errors.
- Configurable retries via env vars or command args (default=3).
- Exceptions do not crash the entire job; individual rows are retried then marked failed in stats.

## Throttling Strategy
- Command-level throttle_seconds default=1.0s between requests to respect Nominatim usage policy.
- Configurable via GEOCODE_THROTTLE env var or --throttle flag.

## Resumability Design
- Command processes only records where is_geocoded=False.
- Coordinates persisted immediately per successful geocode, enabling safe interruption and resume.

## Address Normalization Decisions
- Utilities in utils/geocoding_utils.py build prioritized queries: "Truckstop Name, City, State" with fallback to address.
- Highway-like names are detected and fallback to address to improve matching.

## Coordinate Validation Strategy
- validate_coordinates enforces lat/lon ranges and applies loose USA bounding box (lat 18..72, lon -170..-50) to reject clearly invalid or non-USA results.

## Incremental Persistence Design
- Repository provides update_coordinates which updates DB per successful geocode using queryset.update() for minimal ORM overhead.
- Batch-size limits DB fetches; updates are incremental to avoid big transactions.

## Long-Running Job Considerations
- Streaming DB iteration via iterator() with batch grouping keeps memory low.
- Command logs progress and stats; interruptions (Ctrl-C) are  already-geocoded rows are skipped on resume.safe 

## Spatial Query Preparation
- Coordinates persisted as Decimal fields on FuelStation, preparing the schema for PostGIS migration and spatial indexing later.

## Logging and Observability
- Structured logging via Python logging module; logs include station id, attempts, success/failure and elapsed time in final stats.

## Performance Considerations
- Minimal per-row DB work: select only necessary fields, update using queryset.update.
- bulk_create used in ingestion stage; geocoding updates are incremental per station to ensure resumability.

## Files Added
- fuel_optimizer/apps/route_optimizer/services/geocoding_service.py
- fuel_optimizer/apps/route_optimizer/infrastructure/geocoding/geocoder.py (extended with NominatimGeocoder)
- fuel_optimizer/apps/route_optimizer/utils/geocoding_utils.py
- fuel_optimizer/apps/route_optimizer/management/commands/enrich_fuel_coordinates.py

## Files Modified
- fuel_optimizer/apps/route_optimizer/repositories/fuel_station_repository.py

## Validation Results
- Command ready for use; to run (safe defaults):
  python manage.py enrich_fuel_coordinates --batch 100 --throttle 1.0 --retries 3 --timeout 10.0 --provider noop
- The command is resumable and will skip already geocoded rows.

## Technical Debt
- Consider persistent failure counters to avoid repeating futile attempts.
- Implement tests and CI harness.

## Next Steps
- Implement async, rate-limited worker for higher throughput.
- Add PostGIS-backed spatial repository and spatial indexes.

## Git Commit
feat(geocoding): implement spatial enrichment infrastructure

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
