import mlflow
import os
from dotenv import load_dotenv

load_dotenv()

mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
mlflow_username = os.getenv('MLFLOW_USERNAME')
mlflow_password = os.getenv('MLFLOW_PASSWORD')

print("=== MLflow Configuration ===")
print(f"Tracking URI: {mlflow_tracking_uri}")
print(f"Username: {mlflow_username}")
print(f"Password set: {'Yes' if mlflow_password else 'No (THIS IS THE ISSUE!)'}")

if mlflow_tracking_uri:
    # Set credentials if available
    if mlflow_username and mlflow_password:
        os.environ['MLFLOW_TRACKING_USERNAME'] = mlflow_username
        os.environ['MLFLOW_TRACKING_PASSWORD'] = mlflow_password
    
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    print(f"\n=== Testing Connection ===")
    try:
        # Try to list experiments (this will create default if none exist)
        experiments = mlflow.search_experiments()
        print(f"✅ Connected! Found {len(experiments)} experiments")
        for exp in experiments[:3]:
            print(f"  - {exp.name} (ID: {exp.experiment_id})")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nPossible issues:")
        print("1. MLFLOW_PASSWORD not set in .env")
        print("2. Invalid Dagshub token")
        print("3. Repository doesn't have MLflow enabled")
        print("4. Network/authentication issue")
else:
    print("\n❌ MLFLOW_TRACKING_URI not set")
