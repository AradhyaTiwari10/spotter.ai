# datasets

This folder holds raw datasets used by the project for analysis, ETL staging and testing.

Rules
- Treat files in this folder as read-only raw inputs. Do not modify original raw files in-place; instead, copy into a processing/staging area.
- Do not commit large production datasets to the repository. Keep only small sample or anonymized datasets.

Organization
- datasets/
  - fuel_prices/           # raw fuel price CSVs and historical data
    - fuel-prices-for-be-assessment.csv

ETL expectations
- ETL pipelines should read from datasets/ and write processed outputs to a dedicated data/ or storage service (S3, database).
- Future ETL should include schema validation, checksum verification, and provenance metadata.

Standards
- Use relative paths within the codebase; avoid absolute paths.
- Provide README and schema files alongside raw data.

