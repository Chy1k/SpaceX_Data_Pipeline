# GEMINI.md - SpaceX Data Pipeline Project Context

## Overview
This file serves as the system instruction and context for the Gemini CLI. The goal is to build an end-to-end Data Engineering pipeline using SpaceX API data, progressing from a local environment to a cloud-ready state, implementing all six core pillars of modern data architecture.

**Gemini CLI Instructions:**
1. Read this file to understand the project architecture, current phase, and strict coding standards.
2. When asked for code help, DO NOT provide the exact implementation for the SpaceX pipeline. Provide analogous examples (e.g., using a mock Weather API or E-commerce data) demonstrating the required DE pattern (e.g., pagination, error handling, idempotency).
3. Always explain the *WHY* behind technical decisions, assuming a foundational understanding of Python but treating DE concepts (like partitioning, columnar storage, and orchestrators) as new knowledge that requires objective, clear, and detailed explanations.
4. Proactively guide the user on where they should start creating files and writing code for each step of the project.

---

## Project Architecture: The 6 Pillars

To build a production-grade system, this project implements the six discrete components of a modern data pipeline. The architecture decouples ingestion from business logic to ensure data lineage, recovery, and scalability.

### 1. Ingestion Layer (Extraction)
* **Goal:** Pull data from the SpaceX API (`/v4/launches`, `/v4/rockets`) without breaking the source or duplicating records.
* **Implementation:** Python scripts using the `requests` library.
* **Core Concepts:** Robust HTTP error handling (retries, timeouts) and strict idempotency. Running the extraction twice for the same date must yield the same final state without appending duplicate payloads.
* **The WHY:** Isolating the external API dependency guarantees that downstream processes can continue even if the source API experiences downtime.

### 2. Storage Layer (Persistence)
* **Goal:** Store data through a Medallion Architecture (Bronze, Silver, Gold).
* **Data Lake (Bronze/Silver):** Local filesystem directory structure.
  * **Bronze:** Raw JSON partitioned by date (e.g., `./data/bronze/launches/year=2023/month=05/`).
  * **Silver:** Transformed `.parquet` files. Parquet is a compressed, columnar storage format optimized for analytical queries.
* **Data Warehouse (Gold):** A local DuckDB file (`spacex_warehouse.duckdb`). DuckDB is a high-performance, in-process SQL engine.
* **The WHY:** Storing raw data acts as an insurance policy. If transformation logic changes, data can be reprocessed from the Bronze layer without re-querying the API. Partitioning minimizes the data volume scanned during processing.

### 3. Transformation Engine (Compute)
* **Goal:** Cleanse, structure, and aggregate the data.
* **Bronze to Silver:** Use `pandas` or `polars` to read raw JSON, flatten nested dictionaries (like payload details), enforce data types, and write to Parquet.
* **Silver to Gold:** Use DuckDB SQL to join `launches` and `rockets` tables, creating aggregated analytical views.
* **The WHY:** Raw data contains nulls, nested arrays, and mismatched types. The transformation engine applies the business rules necessary to make the data accurate and queryable.

### 4. Orchestration (Control Flow)
* **Goal:** Manage task dependencies and execution order.
* **Phase 1:** A Bash script (`run_pipeline.sh`) to execute Python files sequentially and handle exit codes.
* **Phase 2:** Apache Airflow (via Docker) using Directed Acyclic Graphs (DAGs) in Python.
* **The WHY:** Silver transformations cannot run if Bronze ingestion fails. An orchestrator manages these dependencies, handles automated retries, and provides execution observability.

### 5. Observability and Data Quality
* **Goal:** Ensure the health of the infrastructure and the accuracy of the data.
* **Observability:** Replace standard prints with Python's `logging` module to track execution times, module states, and error traces.
* **Data Quality:** Leverage Test Automation Engineering (TAE) principles using `pytest`. Write assertions before data enters the Gold layer to verify primary keys are never null, dates are valid, and records are unique.
* **The WHY:** Silent failures (data processing completes, but the data is incorrect) are critical risks. Quality gates catch anomalies before they reach the consumer.

### 6. Serving Layer (Consumption)
* **Goal:** Provide actual value through data visualization.
* **Implementation:** Streamlit (pure Python web framework) or Metabase (open-source BI tool connected locally to DuckDB).
* **The WHY:** Engineering effort must translate into actionable insights. Dashboards proving metrics like "Payload Mass Over Time" validate the end-to-end pipeline.

---

## Analogous Code Examples (For Reference)

*Note to Gemini: Use patterns like this when providing assistance.*

**Example: Robust API Ingestion with Idempotency (Weather API)**

```python
import requests
import json
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure Observability (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_weather_data(date_str: str, output_dir: str):
    """
    Fetches weather data for a specific date.
    Demonstrates idempotency by overwriting existing files for the same date.
    """
    url = f"[https://api.mock-weather.com/v1/historical?date=](https://api.mock-weather.com/v1/historical?date=){date_str}"
    
    # Configure robust error handling with retries
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        logging.info(f"Initiating extraction for date: {date_str}")
        response = session.get(url, timeout=10)
        response.raise_for_status() # Fails fast if the HTTP status is not 200 OK
        data = response.json()
        
        # Idempotent load mechanism: Create directory if it doesn't exist
        partition_path = os.path.join(output_dir, f"date={date_str}")
        os.makedirs(partition_path, exist_ok=True)
        
        file_path = os.path.join(partition_path, "raw_weather.json")
        
        # Overwriting the file ensures idempotency (running it twice yields the same final state)
        with open(file_path, 'w') as f:
            json.dump(data, f)
            
        logging.info(f"Successfully saved data to {file_path}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Pipeline failed during extraction: {e}")
        raise # Rethrow to alert the orchestrator