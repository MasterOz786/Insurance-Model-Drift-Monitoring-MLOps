import mlflow
import os
from dotenv import load_dotenv

load_dotenv()

mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
mlflow_username = os.getenv("MLFLOW_USERNAME")
mlflow_password = os.getenv("MLFLOW_PASSWORD")

if mlflow_tracking_uri:
    # Set credentials for Dagshub authentication
    if mlflow_username and mlflow_password:
        os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_username
        os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_password
    
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    print(f"✅ Tracking URI set: {mlflow_tracking_uri}")
    
    # Test experiment creation
    experiment_name = "Insurance Model Training"
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"✅ Created experiment: {experiment_name} (ID: {experiment_id})")
        else:
            print(f"✅ Experiment exists: {experiment_name} (ID: {experiment.experiment_id})")
        
        mlflow.set_experiment(experiment_name)
        print(f"✅ Experiment set successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTrying alternative method...")
        try:
            mlflow.set_experiment(experiment_name)
            print(f"✅ Experiment set using set_experiment()")
        except Exception as e2:
            print(f"❌ Failed: {str(e2)}")
else:
    print("❌ MLFLOW_TRACKING_URI not set")
