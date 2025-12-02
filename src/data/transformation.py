"""
Data Transformation Module
Transforms raw insurance data through cleaning and feature engineering
"""

import numpy as np
import pandas as pd
import os
import logging
from datetime import datetime
from sklearn.impute import SimpleImputer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Cleaner:
    def __init__(self):
        self.imputer = SimpleImputer(strategy="most_frequent", missing_values=np.nan)

    def clean_data(self, data):
        data.drop(
            ["id", "SalesChannelID", "VehicleAge", "DaysSinceCreated"],
            axis=1,
            inplace=True,
        )

        data["AnnualPremium"] = (
            data["AnnualPremium"]
            .str.replace("£", "")
            .str.replace(",", "")
            .astype(float)
        )

        for col in ["Gender", "RegionID"]:
            data[col] = self.imputer.fit_transform(data[[col]]).flatten()

        data["Age"] = data["Age"].fillna(data["Age"].median())
        data["HasDrivingLicense"] = data["HasDrivingLicense"].fillna(1)
        data["Switch"] = data["Switch"].fillna(-1)
        data["PastAccident"] = data["PastAccident"].fillna("Unknown", inplace=False)

        Q1 = data["AnnualPremium"].quantile(0.25)
        Q3 = data["AnnualPremium"].quantile(0.75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR
        data = data[data["AnnualPremium"] <= upper_bound]

        return data


def transform_data(**context) -> str:
    """
    Transform raw insurance data through cleaning and feature engineering.
    Loads data from raw directory, applies transformations, and saves to processed directory.

    Args:
        **context: Airflow context (optional)

    Returns:
        str: Path to saved processed data file
    """
    try:
        # Determine input file - check for insurance data in raw directory
        # Priority: production.csv > latest_extract.csv (if it's insurance data)
        input_paths = [
            "data/raw/production.csv",
            "data/production.csv",
            "data/raw/latest_extract.csv",
        ]

        input_path = None
        for path in input_paths:
            if os.path.exists(path):
                # Check if it's insurance data (has AnnualPremium column)
                try:
                    sample = pd.read_csv(path, nrows=1)
                    if "AnnualPremium" in sample.columns:
                        input_path = path
                        break
                except:
                    continue

        if input_path is None:
            # Fallback to train.csv for testing
            if os.path.exists("data/train.csv"):
                input_path = "data/train.csv"
                logger.warning("Using train.csv as input (no production data found)")
            else:
                raise FileNotFoundError(
                    "No insurance data found. Expected one of: "
                    "data/raw/production.csv, data/production.csv, or data/train.csv"
                )

        logger.info(f"Loading data from {input_path}")
        df = pd.read_csv(input_path)

        logger.info(f"Original data shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")

        # Check if this is insurance data
        if "AnnualPremium" not in df.columns:
            raise ValueError(
                f"Data does not appear to be insurance data. "
                f"Expected 'AnnualPremium' column but found: {list(df.columns)}"
            )

        # Apply transformations
        logger.info("Applying data transformations...")
        cleaner = Cleaner()
        df_processed = cleaner.clean_data(df.copy())

        logger.info(f"Processed data shape: {df_processed.shape}")
        logger.info(f"Removed {len(df) - len(df_processed)} rows (outliers)")

        # Ensure processed directory exists
        os.makedirs("data/processed", exist_ok=True)

        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/processed/processed_{timestamp}.csv"
        df_processed.to_csv(output_path, index=False)
        logger.info(f"Processed data saved to: {output_path}")

        # Also save as 'latest' for downstream tasks
        latest_path = "data/processed/latest.csv"
        df_processed.to_csv(latest_path, index=False)
        logger.info(f"Processed data also saved to: {latest_path}")

        logger.info(f"✓ Transformation completed successfully")
        logger.info(f"  - Input: {input_path}")
        logger.info(f"  - Output: {latest_path}")
        logger.info(f"  - Rows: {len(df)} → {len(df_processed)}")
        logger.info(f"  - Columns: {len(df.columns)} → {len(df_processed.columns)}")

        return latest_path

    except Exception as e:
        logger.error(f"Data transformation failed: {str(e)}")
        raise


if __name__ == "__main__":
    # For local testing
    print("Running data transformation...")
    try:
        result = transform_data()
        print(f"✅ Success! Processed data saved to: {result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
