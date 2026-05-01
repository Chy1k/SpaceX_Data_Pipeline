# SpaceX Data Pipeline 🚀

An end-to-end Data Engineering pipeline built with Python, DuckDB, and Streamlit. This project implements a **Medallion Architecture** to ingest SpaceX API data, transform it into optimized Parquet format, and provide failure analysis insights via an interactive dashboard.

## 🏗️ Architecture: The 6 Pillars
1. **Ingestion Layer:** Robust, idempotent extraction from SpaceX API using `requests` with retry logic.
2. **Storage Layer:** Medallion Architecture (Bronze JSON -> Silver Parquet -> Gold DuckDB).
3. **Transformation Engine:** Data cleaning and flattening with `pandas` and analytical modeling with `DuckDB` SQL.
4. **Orchestration:** Automated control flow using a Bash orchestrator (`run_pipeline.sh`).
5. **Observability & Data Quality:** centralized logging and automated quality gates using `pytest`.
6. **Serving Layer:** Interactive BI dashboard built with `Streamlit`.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Chy1k/SpaceX_Data_Pipeline.git
   cd SpaceX_Data_Pipeline
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Pipeline
To execute the entire pipeline (Ingest -> Transform -> Test -> Warehouse), run:
```bash
bash orchestration/run_pipeline.sh
```

### Viewing the Dashboard
Once the pipeline has completed, launch the Streamlit dashboard:
```bash
python -m streamlit run src/serving/app.py
```

## 📊 Data Quality Gates
The pipeline includes automated tests to ensure:
- **Uniqueness:** No duplicate launch records.
- **Completeness:** No missing rocket IDs for critical analysis.
- **Validity:** Correct data types and success flags.

## 🛠️ Tech Stack
- **Language:** Python
- **Storage:** Parquet, DuckDB
- **Libraries:** Pandas, Requests, Pytest, Streamlit
- **Orchestration:** Bash (Phase 1)
