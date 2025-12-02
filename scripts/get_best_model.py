"""
Get Best Model Version from MLflow
Returns the version of the production model for deployment
"""

import os
import sys
import warnings

# Suppress MLflow deprecation warnings before importing
warnings.filterwarnings("ignore", category=FutureWarning)

import mlflow
from dotenv import load_dotenv
from mlflow.tracking import MlflowClient

# Load environment variables
load_dotenv()

# Set up MLflow
mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
mlflow_username = os.getenv("MLFLOW_USERNAME")
mlflow_password = os.getenv("MLFLOW_PASSWORD")

if not mlflow_tracking_uri:
    print("MLFLOW_TRACKING_URI not set", file=sys.stderr)
    sys.exit(1)

if mlflow_username and mlflow_password:
    os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_username
    os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_password

mlflow.set_tracking_uri(mlflow_tracking_uri)

model_name = os.getenv("MODEL_NAME", "insurance_model")
client = MlflowClient()

try:
    # Try to get latest production model
    try:
        prod_models = client.get_latest_versions(model_name, stages=["Production"])
    except Exception as e:
        # If model registry not available, try staging
        prod_models = []

    if not prod_models:
        # Fallback to Staging if no Production model
        try:
            prod_models = client.get_latest_versions(model_name, stages=["Staging"])
        except Exception as e:
            # If no staging, try to get latest version without stage
            try:
                # Get all versions and use latest
                all_versions = client.search_model_versions(f"name='{model_name}'")
                if all_versions:
                    # Sort by version number (descending) and get latest
                    sorted_versions = sorted(
                        all_versions, key=lambda x: int(x.version), reverse=True
                    )
                    if sorted_versions:
                        print(sorted_versions[0].version)
                        sys.exit(0)
            except:
                pass

    if not prod_models:
        print("No production or staging model found", file=sys.stderr)
        print("Please train and register a model first", file=sys.stderr)
        sys.exit(1)

    model = prod_models[0]
    print(model.version)

except Exception as e:
    print(f"Error getting model version: {str(e)}", file=sys.stderr)
    import traceback

    traceback.print_exc()
    sys.exit(1)
