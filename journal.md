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
