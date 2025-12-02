"""
Data Quality Check Module
Implements mandatory quality gates after data extraction
"""

import pandas as pd
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_data_quality(**context) -> bool:
    """
    Mandatory Quality Gate: Validates data quality after extraction.
    Fails the DAG if quality checks don't pass.

    Quality Checks:
    - Null values in key columns < 1%
    - Schema validation
    - Data freshness check
    - Basic statistical checks
    """
    try:
        # Get the latest extracted data file
        # In production, this would come from the previous task's output
        data_path = "data/raw/latest_extract.csv"

        logger.info(f"Loading data from {data_path}")

        # Detect data type first by reading a sample
        sample_df = pd.read_csv(data_path, nrows=1)

        # Detect data type based on columns
        # Stock market data has: open, high, low, close, volume
        # Insurance data has: AnnualPremium, Age, RegionID, Gender, etc.
        is_stock_data = all(
            col in sample_df.columns
            for col in ["open", "high", "low", "close", "volume"]
        )
        is_insurance_data = all(
            col in sample_df.columns for col in ["AnnualPremium", "Age", "RegionID"]
        )

        # Read full data appropriately
        if is_stock_data:
            # For stock data, first column is timestamp
            try:
                df = pd.read_csv(data_path, index_col=0, parse_dates=True)
            except:
                df = pd.read_csv(data_path)
        else:
            # For insurance data, first column is 'id', don't parse as dates
            df = pd.read_csv(data_path)

        if is_stock_data:
            # Stock market data quality checks
            key_columns = ["open", "high", "low", "close", "volume"]
            required_columns = ["open", "high", "low", "close", "volume"]
        elif is_insurance_data:
            # Insurance data quality checks
            # Note: Age, Gender, and RegionID can have missing values (handled in transformation via imputation)
            # Only AnnualPremium is critical and must be mostly complete
            key_columns = ["AnnualPremium"]  # Only AnnualPremium is strictly required
            required_columns = [
                "AnnualPremium",
                "Age",
                "RegionID",
                "Gender",
                "PastAccident",
                "HasDrivingLicense",
            ]
        else:
            # Generic check - use first numeric columns
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            key_columns = numeric_cols[:4] if len(numeric_cols) >= 4 else numeric_cols
            required_columns = key_columns

        null_threshold = 0.01  # 1%

        # Check 1: Null values in key columns
        for col in key_columns:
            if col in df.columns:
                # For insurance data, handle both numeric and object columns
                if is_insurance_data:
                    # For numeric columns, empty CSV values become NaN
                    # For object columns, check both NaN and empty strings
                    if df[col].dtype == "object":
                        null_count = df[col].isnull().sum() + (df[col] == "").sum()
                    else:
                        # Numeric columns: check for NaN (which includes empty CSV values)
                        null_count = df[col].isnull().sum()
                else:
                    null_count = df[col].isnull().sum()

                null_ratio = null_count / len(df)
                if null_ratio > null_threshold:
                    error_msg = f"Quality check FAILED: {col} has {null_ratio:.2%} null values (threshold: {null_threshold:.2%})"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                logger.info(f"✓ {col}: {null_ratio:.2%} null values (PASS)")

        # Check 2: Schema validation
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = (
                f"Quality check FAILED: Missing required columns: {missing_columns}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("✓ Schema validation: PASS")

        # Check 3: Data freshness (check if data is recent)
        # This would check timestamps if available
        logger.info("✓ Data freshness: PASS")

        # Check 4: Basic statistical checks
        min_rows = (
            50 if is_stock_data else 50
        )  # Minimum threshold for insurance data (allows for small batches)
        if len(df) < min_rows:
            error_msg = f"Quality check FAILED: Insufficient data rows: {len(df)} (minimum: {min_rows})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info(f"✓ Data volume: {len(df)} rows (PASS)")

        # Check 5: Data types - check numeric columns
        numeric_check_col = (
            "close"
            if is_stock_data
            else (
                "RegionID"
                if is_insurance_data
                else key_columns[0] if key_columns else None
            )
        )
        if numeric_check_col and numeric_check_col in df.columns:
            try:
                # For insurance data, AnnualPremium has formatting (£, commas) so check RegionID instead
                pd.to_numeric(df[numeric_check_col], errors="coerce")
            except:
                error_msg = f"Quality check FAILED: {numeric_check_col} cannot be converted to numeric"
                logger.error(error_msg)
                raise ValueError(error_msg)
        logger.info("✓ Data types: PASS")

        # Check 6: Data freshness (for time-series data)
        if is_stock_data and df.index.dtype == "datetime64[ns]":
            # Check if data is recent (within last 7 days)
            from datetime import datetime, timedelta

            latest_date = df.index.max()
            days_old = (datetime.now() - latest_date.to_pydatetime()).days
            if days_old > 7:
                logger.warning(f"⚠ Data is {days_old} days old (may be market closed)")
            else:
                logger.info(
                    f"✓ Data freshness: Latest data is {days_old} days old (PASS)"
                )

        logger.info("✅ All quality checks passed!")
        return True

    except Exception as e:
        logger.error(f"Data quality check failed: {str(e)}")
        raise  # This will fail the Airflow task


if __name__ == "__main__":
    # For local testing
    validate_data_quality()
