import duckdb
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 

def create_gold_warehouse(silver_dir: str, gold_db_path: str):
    """Connect to Silver via DuckDB, run analytical queries, and save results to Gold database"""
    try:
        logging.info(f"Connecting to DuckDB at {gold_db_path}...")
        
        conn = duckdb.connect(gold_db_path)
        silver_dir_posix = silver_dir.replace("\\", "/")
        parquet_glob = f"{silver_dir_posix}/ingestion_date=*/*.parquet"

        logging.info(f"Reading from Silver Parquet: {parquet_glob}")

        # Create a table of all launches
        conn.execute(f"""
            CREATE OR REPLACE TABLE fact_launches AS
            SELECT * FROM read_parquet('{parquet_glob}');
        """)

        # Create aggregated table
        conn.execute("""
            CREATE OR REPLACE TABLE agg_rocket_failure_analysis AS
            SELECT
                rocket as rocket_id,
                COUNT(*) as total_launches,
                SUM(CASE WHEN success = false THEN 1 ELSE 0 END) as total_failures,
                ROUND(SUM(CASE WHEN success = false THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as failure_rate_pct      
            FROM fact_launches
            WHERE rocket IS NOT NULL
            GROUP BY rocket
            ORDER BY failure_rate_pct DESC, total_launches DESC
        """)

        logging.info("Successfully built Gold layer warehouse.")
        conn.close()
        return True

    except Exception as e:
        logging.error(f"Error in Silver to Gold transformation: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    silver_dir = os.path.join(current_script_dir, "..", "..", "data", "silver", "launches")
    gold_db_path = os.path.join(current_script_dir, "..", "..", "data", "gold", "spacex_data.duckdb")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(gold_db_path), exist_ok=True)
    
    try:
        create_gold_warehouse(silver_dir, gold_db_path)
    except Exception as e:
        logging.error(f"Gold transformation failed: {e}")
        raise

if __name__ == "__main__":
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    silver_dir = os.path.join(current_script_dir, "..", "..", "data", "silver", "launches")
    gold_db_path = os.path.join(current_script_dir, "..", "..", "data", "gold", "spacex_data.duckdb")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(gold_db_path), exist_ok=True)
    
    try:
        create_gold_warehouse(silver_dir, gold_db_path)
    except Exception as e:
        logging.error(f"Gold transformation failed: {e}")
        raise