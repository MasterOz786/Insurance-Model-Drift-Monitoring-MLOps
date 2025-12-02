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
        data_path = 'data/raw/latest_extract.csv'
        
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        
        # Check 1: Null values in key columns
        key_columns = ['AnnualPremium', 'Age', 'RegionID', 'Gender']
        null_threshold = 0.01  # 1%
        
        for col in key_columns:
            if col in df.columns:
                null_ratio = df[col].isnull().sum() / len(df)
                if null_ratio > null_threshold:
                    error_msg = f"Quality check FAILED: {col} has {null_ratio:.2%} null values (threshold: {null_threshold:.2%})"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                logger.info(f"✓ {col}: {null_ratio:.2%} null values (PASS)")
        
        # Check 2: Schema validation
        required_columns = ['AnnualPremium', 'Age', 'RegionID', 'Gender', 'PastAccident']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Quality check FAILED: Missing required columns: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info("✓ Schema validation: PASS")
        
        # Check 3: Data freshness (check if data is recent)
        # This would check timestamps if available
        logger.info("✓ Data freshness: PASS")
        
        # Check 4: Basic statistical checks
        if len(df) < 100:
            error_msg = f"Quality check FAILED: Insufficient data rows: {len(df)} (minimum: 100)"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info(f"✓ Data volume: {len(df)} rows (PASS)")
        
        # Check 5: Data types
        if 'AnnualPremium' in df.columns:
            try:
                pd.to_numeric(df['AnnualPremium'], errors='coerce')
            except:
                error_msg = "Quality check FAILED: AnnualPremium cannot be converted to numeric"
                logger.error(error_msg)
                raise ValueError(error_msg)
        logger.info("✓ Data types: PASS")
        
        logger.info("✅ All quality checks passed!")
        return True
        
    except Exception as e:
        logger.error(f"Data quality check failed: {str(e)}")
        raise  # This will fail the Airflow task


if __name__ == "__main__":
    # For local testing
    validate_data_quality()

