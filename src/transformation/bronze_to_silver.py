import pandas as pd
import os
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def flatten_spacex_data(input_dir: str, output_dir: str):
    """Load raw SpaceX JSON data from Bronze, flatten nested structures, and save to Silver as Parquet.
    """
    try:
        logging.info(f"Starting transformation for directory: {input_dir}")
        
        # 1. Read the raw JSON
        with open(input_dir, 'r') as f:
            data = json.load(f)
        df_flat = pd.json_normalize(data["docs"])

        # 3. Extract date partition
        df_flat["ingestion_date"] = pd.to_datetime(df_flat["date_utc"].str.split("T").str[0])
        
        # 4. Create the output directory
        partition_path = os.path.join(output_dir, f"ingestion_date={df_flat['ingestion_date'].iloc[0].strftime('%Y-%m-%d')}")
        os.makedirs(partition_path, exist_ok=True)
        
        # 5. Save to Silver (Parquet)
        output_file = os.path.join(partition_path, "spacex_launches_silver.parquet")
        df_flat.to_parquet(output_file, index=False)
        
        logging.info(f"Successfully transformed and saved {len(df_flat)} records to {output_file}")
        return output_file
        
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        raise

if __name__ == "__main__":
    from datetime import datetime
    
    # Use today's date for the extraction run
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Safely construct the path to our Bronze storage layer
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    bronze_dir = os.path.join(current_script_dir, "..", "..", "data", "bronze", "launches", f"date={today_str}", "spacex_launches.json")
    silver_dir = os.path.join(current_script_dir, "..", "..", "data", "silver", "launches")
    
    # Ensure the directory exists
    os.makedirs(silver_dir, exist_ok=True)
    
    try:
        flatten_spacex_data(bronze_dir, silver_dir)
    except Exception as e:
        logging.error(f"Transformation failed: {e}")
        raise
