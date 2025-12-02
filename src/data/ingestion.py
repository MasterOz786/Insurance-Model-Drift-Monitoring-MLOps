"""
Data Ingestion Module
Extracts insurance data from production source (simulates API/data source)
"""

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_data(**context):
    """
    Extract insurance data from production source.
    Simulates fetching new insurance policy data for drift monitoring.

    Args:
        **context: Airflow context (optional)

    Returns:
        str: Path to saved data file
    """
    try:
        # Check if we should use existing production data or generate synthetic
        use_existing = os.getenv("USE_EXISTING_DATA", "true").lower() == "true"
        num_samples = int(os.getenv("NUM_SAMPLES", "100"))

        if use_existing and os.path.exists("data/production.csv"):
            logger.info("Loading data from existing production.csv file")
            df = pd.read_csv("data/production.csv")

            # Sample random rows to simulate new incoming data
            if len(df) > num_samples:
                df = df.sample(n=num_samples, random_state=None).reset_index(drop=True)
                logger.info(f"Sampled {num_samples} records from production data")
            else:
                logger.info(f"Using all {len(df)} records from production data")
        else:
            # Generate synthetic insurance data
            logger.info(f"Generating {num_samples} synthetic insurance records")
            df = _generate_synthetic_insurance_data(num_samples)

        # Add extraction timestamp
        df["extraction_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ensure data directory exists
        os.makedirs("data/raw", exist_ok=True)

        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/raw/latest_extract_{timestamp}.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to: {output_path}")

        # Also save as 'latest' for quality check and transformation
        df.to_csv("data/raw/latest_extract.csv", index=False)
        logger.info(f"Data also saved to: data/raw/latest_extract.csv")

        logger.info(f"Successfully extracted {len(df)} insurance records")
        logger.info(f"Columns: {list(df.columns)}")

        return output_path

    except Exception as e:
        logger.error(f"Data extraction failed: {str(e)}")
        raise


def _generate_synthetic_insurance_data(n_samples=100):
    """
    Generate synthetic insurance data matching the production schema

    Args:
        n_samples: Number of records to generate

    Returns:
        DataFrame with insurance data
    """
    np.random.seed(int(datetime.now().timestamp()) % 2**32)

    # Generate data matching the insurance schema
    data = {
        "id": range(100000, 100000 + n_samples),
        "Gender": np.random.choice(
            ["Male", "Female", ""], n_samples, p=[0.5, 0.45, 0.05]
        ),
        "Age": np.random.normal(35, 15, n_samples).clip(18, 80),
        "HasDrivingLicense": np.random.choice([1.0, 0.0], n_samples, p=[0.95, 0.05]),
        "RegionID": np.random.choice(range(1, 51), n_samples),
        "Switch": np.random.choice([1.0, 0.0, np.nan], n_samples, p=[0.4, 0.4, 0.2]),
        "VehicleAge": np.random.choice(
            ["< 1 Year", "1-2 Year", "> 2 Year", ""],
            n_samples,
            p=[0.4, 0.3, 0.25, 0.05],
        ),
        "PastAccident": np.random.choice(
            ["Yes", "No", ""], n_samples, p=[0.3, 0.6, 0.1]
        ),
        "AnnualPremium": [
            f"£{np.random.uniform(100, 5000):,.2f} " for _ in range(n_samples)
        ],
        "SalesChannelID": np.random.choice([26, 124, 152, 154, 156, 160], n_samples),
        "DaysSinceCreated": np.random.randint(1, 365, n_samples),
        "Result": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
    }

    df = pd.DataFrame(data)

    # Introduce some missing values
    missing_indices = np.random.choice(
        df.index, size=int(n_samples * 0.1), replace=False
    )
    for idx in missing_indices[: len(missing_indices) // 3]:
        df.loc[idx, "Gender"] = ""
    for idx in missing_indices[
        len(missing_indices) // 3 : 2 * len(missing_indices) // 3
    ]:
        df.loc[idx, "Switch"] = np.nan
    for idx in missing_indices[2 * len(missing_indices) // 3 :]:
        df.loc[idx, "PastAccident"] = ""

    return df


# For backward compatibility with existing code
class Ingestion:
    """Legacy class for backward compatibility"""

    def __init__(self):
        import yaml

        with open("config.yml", "r") as file:
            self.config = yaml.safe_load(file)

    def load_data(self):
        """Load data from CSV files (for existing insurance model)"""
        train_data_path = self.config["data"]["train_path"]
        test_data_path = self.config["data"]["test_path"]
        train_data = pd.read_csv(train_data_path)
        test_data = pd.read_csv(test_data_path)
        return train_data, test_data


if __name__ == "__main__":
    # For local testing
    print("Testing insurance data extraction...")
    try:
        result = extract_data()
        print(f"✅ Success! Data saved to: {result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
