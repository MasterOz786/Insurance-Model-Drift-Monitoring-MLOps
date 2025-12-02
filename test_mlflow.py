import mlflow
import os
from dotenv import load_dotenv

load_dotenv()

mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
mlflow_username = os.getenv('MLFLOW_USERNAME')
mlflow_password = os.getenv('MLFLOW_PASSWORD')

print(f"Tracking URI: {mlflow_tracking_uri}")
print(f"Username: {mlflow_username}")
print(f"Password set: {'Yes' if mlflow_password else 'No'}")

if mlflow_tracking_uri:
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    print(f"\n✅ MLflow configured!")
    print(f"Current tracking URI: {mlflow.get_tracking_uri()}")
else:
    print("\n❌ MLFLOW_TRACKING_URI not set")
