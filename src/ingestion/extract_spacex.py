import requests
import json 
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_spacex_data(date_str: str, output_dir: str):
    API_URL = "https://api.spacexdata.com/v5/launches/query"

    # Set up HTTP session with retry logic 
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)

    # Query for all launches, limited to 5000 (max by API)
    query = {
        "query": {},
        "options": {
            "pagination": False,
            "limit": 5000
        }
    }
    try:
        logging.info("Fetching data for all SpaceX launches...")
        response = session.post(API_URL, json=query, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()
        logging.info(f"Successfully fetched {len(data['docs'])} launches.")

        # Create the partition directory inside the dynamically provided output_dir
        # VERIFIED: Correct Medallion Architecture partitioning
        partition_path = os.path.join(output_dir, f"date={date_str}")
        os.makedirs(partition_path, exist_ok=True)

        # Define the file path inside the partition folder
        output_path = os.path.join(partition_path, "spacex_launches.json")
        # Write data to file
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logging.info(f"Data saved to {output_path}")

        return output_path
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        raise

if __name__ == "__main__":
    from datetime import datetime
    
    # Use today's date for the extraction run
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Safely construct the path to our Bronze storage layer
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    bronze_dir = os.path.join(current_script_dir, "..", "..", "data", "bronze", "launches")
    
    # Ensure the directory exists
    os.makedirs(bronze_dir, exist_ok=True)

    try:
        fetch_spacex_data(today_str, bronze_dir)
    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        raise