import mlflow
import os
from dotenv import load_dotenv

load_dotenv()

# Show what endpoint is being called
print("=== MLflow Endpoint Analysis ===\n")

# Check MLflow version
import mlflow.version
print(f"MLflow version: {mlflow.__version__}")

# Check tracking URI
mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
print(f"Tracking URI: {mlflow_tracking_uri}\n")

# The error shows it's calling CreateLoggedModel endpoint
print("=== Endpoint Being Called ===")
print("Endpoint: /api/2.0/mlflow/logged-models/create")
print("Method: POST")
print("Purpose: Create a logged model entry in MLflow")
print("\nThis is called internally by mlflow.sklearn.log_model()")
print("when it tries to register the model metadata.")

# Check what MLflow client would call
from mlflow.tracking import MlflowClient
from mlflow.store.tracking.rest_store import RestStore

print("\n=== MLflow Internal Call ===")
print("When you call: mlflow.sklearn.log_model(model, 'model')")
print("MLflow internally calls:")
print("  - MlflowClient()._create_logged_model()")
print("  - Which calls: RestStore.create_logged_model()")
print("  - Which makes HTTP POST to: /api/2.0/mlflow/logged-models/create")
print("\nThis endpoint is NOT supported by Dagshub's MLflow backend.")
