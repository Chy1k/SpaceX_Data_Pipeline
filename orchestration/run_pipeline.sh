#!/bin/bash
# SpaceX Data Pipeline Orchestrator

echo "Starting SpaceX Data Pipeline..."

# Exit immediately if a command exits with a non-zero status
set -e

echo "--- Running Ingestion (Bronze Layer) ---"
python src/ingestion/extract_spacex.py

echo "--- Running Transformation (Silver Layer) ---"
python src/transformation/bronze_to_silver.py

echo "--- Running Data Warehouse (Gold Layer) ---"
python src/transformation/silver_to_gold.py

echo "--- Pipeline execution complete! ---"
echo "To view the dashboard, run: python -m streamlit run src/serving/app.py"
