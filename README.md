# SpaceX Data Pipeline

An end-to-end Data Engineering pipeline using SpaceX API data.

## Architecture
- **Pillar 1: Ingestion Layer** - Python scripts pulling from SpaceX API.
- **Pillar 2: Storage Layer** - Medallion Architecture (Bronze/Silver/Gold).
- **Pillar 3: Transformation Engine** - pandas/polars and DuckDB.
- **Pillar 4: Orchestration** - Bash script (moving to Airflow later).
- **Pillar 5: Observability and Data Quality** - Python logging and pytest.
- **Pillar 6: Serving Layer** - Streamlit or Metabase dashboards.
