"""
Data Drift Detection Module
Detects out-of-distribution features in incoming requests
"""

import pandas as pd
import numpy as np
import logging
import os
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reference statistics (would be loaded from training data)
REFERENCE_STATS = {
    "AnnualPremium": {"mean": 1500, "std": 500, "min": 0, "max": 5000},
    "Age": {"mean": 45, "std": 15, "min": 18, "max": 100},
    "RegionID": {"mean": 50, "std": 20, "min": 1, "max": 100},
}


def load_reference_stats(stats_path: str = "data/reference_stats.pkl"):
    """Load reference statistics from training data"""
    if os.path.exists(stats_path):
        return joblib.load(stats_path)
    return REFERENCE_STATS


def check_feature_drift(
    feature_name: str, value: float, z_threshold: float = 3.0
) -> bool:
    """
    Check if a feature value is out of distribution (drift)

    Args:
        feature_name: Name of the feature
        value: Feature value to check
        z_threshold: Z-score threshold for drift detection (default: 3.0 = 3 sigma)

    Returns:
        bool: True if drift detected, False otherwise
    """
    stats = load_reference_stats()

    if feature_name not in stats:
        logger.warning(f"No reference stats for feature: {feature_name}")
        return False

    ref_stats = stats[feature_name]

    # Calculate Z-score
    if ref_stats["std"] > 0:
        z_score = abs((value - ref_stats["mean"]) / ref_stats["std"])
    else:
        z_score = 0

    # Check if value is within expected range
    in_range = ref_stats["min"] <= value <= ref_stats["max"]

    # Drift detected if Z-score exceeds threshold or value is out of range
    is_drift = z_score > z_threshold or not in_range

    if is_drift:
        logger.warning(
            f"Drift detected in {feature_name}: value={value}, "
            f"z_score={z_score:.2f}, range=[{ref_stats['min']}, {ref_stats['max']}]"
        )

    return is_drift


def calculate_drift_ratio(
    feature_name: str, values: pd.Series, window_size: int = 100
) -> float:
    """
    Calculate the ratio of drifted values in a sliding window

    Args:
        feature_name: Name of the feature
        values: Series of feature values
        window_size: Size of the sliding window

    Returns:
        float: Ratio of drifted values (0.0 to 1.0)
    """
    if len(values) == 0:
        return 0.0

    recent_values = values.tail(window_size)
    drift_count = sum([check_feature_drift(feature_name, val) for val in recent_values])

    return drift_count / len(recent_values)
