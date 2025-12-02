"""
Model Training Module with MLflow Integration
Trains models and logs experiments to MLflow (Dagshub)
"""

import os
import joblib
import yaml
import pandas as pd
import mlflow
import mlflow.sklearn
import logging
import subprocess
import json
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Trainer:
    def __init__(self):
        self.config = self.load_config()
        self.model_name = self.config["model"]["name"]
        self.model_params = self.config["model"]["params"]
        self.model_path = self.config["model"]["store_path"]
        self.pipeline = self.create_pipeline()

    def load_config(self):
        with open("config.yml", "r") as config_file:
            return yaml.safe_load(config_file)

    def create_pipeline(self):
        preprocessor = ColumnTransformer(
            transformers=[
                ("minmax", MinMaxScaler(), ["AnnualPremium"]),
                ("standardize", StandardScaler(), ["Age", "RegionID"]),
                (
                    "onehot",
                    OneHotEncoder(handle_unknown="ignore"),
                    ["Gender", "PastAccident"],
                ),
            ]
        )

        smote = SMOTE(sampling_strategy=1.0)

        model_map = {
            "RandomForestClassifier": RandomForestClassifier,
            "DecisionTreeClassifier": DecisionTreeClassifier,
            "GradientBoostingClassifier": GradientBoostingClassifier,
        }

        model_class = model_map[self.model_name]
        model = model_class(**self.model_params)

        pipeline = Pipeline(
            [("preprocessor", preprocessor), ("smote", smote), ("model", model)]
        )

        return pipeline

    def feature_target_separator(self, data):
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]
        return X, y

    def train_model(self, X_train, y_train):
        self.pipeline.fit(X_train, y_train)

    def save_model(self):
        model_file_path = os.path.join(self.model_path, "model.pkl")
        os.makedirs(self.model_path, exist_ok=True)
        joblib.dump(self.pipeline, model_file_path)


def train_model(**context):
    """
    Train model with MLflow tracking.
    Loads processed data, trains model, logs to MLflow, and registers model.

    Args:
        **context: Airflow context (optional)

    Returns:
        str: Model URI in MLflow
    """
    try:
        # Load configuration
        with open("config.yml", "r") as f:
            config = yaml.safe_load(f)

        # Set up MLflow tracking
        mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        mlflow_username = os.getenv("MLFLOW_USERNAME")
        mlflow_password = os.getenv("MLFLOW_PASSWORD")

        if mlflow_tracking_uri:
            # Set credentials for Dagshub authentication
            if mlflow_username and mlflow_password:
                os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_username
                os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_password

            mlflow.set_tracking_uri(mlflow_tracking_uri)
            logger.info(f"MLflow tracking URI: {mlflow_tracking_uri}")
        else:
            # Fallback to local
            mlruns_path = os.path.abspath(os.path.join(os.getcwd(), "mlruns"))
            mlflow.set_tracking_uri(f"file://{mlruns_path}")
            logger.warning("MLFLOW_TRACKING_URI not set, using local storage")

        # Set experiment (create if doesn't exist)
        experiment_name = os.getenv(
            "MLFLOW_EXPERIMENT_NAME", "Insurance Model Training"
        )
        try:
            # Try to get existing experiment
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                # Create new experiment
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(
                    f"Created new experiment: {experiment_name} (ID: {experiment_id})"
                )
            else:
                logger.info(
                    f"Using existing experiment: {experiment_name} (ID: {experiment.experiment_id})"
                )
            mlflow.set_experiment(experiment_name)
        except Exception as e:
            # If get_experiment_by_name fails, try set_experiment (creates if needed)
            logger.warning(
                f"Could not get experiment by name: {str(e)}, trying to create..."
            )
            try:
                mlflow.set_experiment(experiment_name)
            except Exception as e2:
                logger.error(f"Failed to set experiment: {str(e2)}")
                raise

        # Load processed data
        processed_data_path = "data/processed/latest.csv"
        if not os.path.exists(processed_data_path):
            raise FileNotFoundError(f"Processed data not found: {processed_data_path}")

        logger.info(f"Loading processed data from {processed_data_path}")
        df = pd.read_csv(processed_data_path)
        logger.info(f"Loaded {len(df)} records")

        # Separate features and target
        X = df.drop("Result", axis=1)
        y = df["Result"]

        # Split data
        test_size = config.get("train", {}).get("test_size", 0.2)
        random_state = config.get("train", {}).get("random_state", 42)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        logger.info(f"Train set: {len(X_train)}, Test set: {len(X_test)}")

        # Start MLflow run
        with mlflow.start_run() as run:
            # Initialize trainer
            trainer = Trainer()

            # Log parameters
            mlflow.log_params(trainer.model_params)
            mlflow.log_param("model_name", trainer.model_name)
            mlflow.log_param("test_size", test_size)
            mlflow.log_param("random_state", random_state)
            mlflow.log_param("train_samples", len(X_train))
            mlflow.log_param("test_samples", len(X_test))

            # Log tags
            mlflow.set_tag("model_type", trainer.model_name)
            mlflow.set_tag(
                "preprocessing", "StandardScaler, MinMaxScaler, OneHotEncoder, SMOTE"
            )
            mlflow.set_tag("data_source", "processed/latest.csv")

            # Step II-3: DVC+MLflow Lineage - Track dataset version
            try:
                # Get git commit hash
                git_commit = (
                    subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
                    )
                    .decode()
                    .strip()
                )
                mlflow.set_tag("git_commit", git_commit)
                logger.info(f"Logged git commit: {git_commit[:8]}")

                # Get DVC directory hash (entire data directory is tracked)
                dvc_file_path = "data.dvc"
                if os.path.exists(dvc_file_path):
                    with open(dvc_file_path, "r") as f:
                        dvc_data = yaml.safe_load(f)
                        if "outs" in dvc_data and len(dvc_data["outs"]) > 0:
                            # Get the hash for the entire data directory
                            dvc_hash = dvc_data["outs"][0].get("md5", "unknown")
                            dvc_size = dvc_data["outs"][0].get("size", 0)
                            dvc_nfiles = dvc_data["outs"][0].get("nfiles", 0)

                            mlflow.set_tag("dvc_data_hash", dvc_hash)
                            mlflow.set_tag("dvc_data_path", "data/")
                            mlflow.set_tag("dvc_data_size", str(dvc_size))
                            mlflow.set_tag("dvc_data_nfiles", str(dvc_nfiles))
                            mlflow.log_param(
                                "dvc_data_hash", dvc_hash
                            )  # Also as param for searchability

                            logger.info(
                                f"Logged DVC data directory hash: {dvc_hash[:8]}... "
                                f"({dvc_nfiles} files, {dvc_size/1024/1024:.2f} MB)"
                            )
                else:
                    logger.warning(
                        "data.dvc file not found - data directory not versioned with DVC"
                    )
            except Exception as e:
                logger.warning(f"Could not get DVC/Git lineage info: {str(e)}")

            # Train model
            logger.info(f"Training {trainer.model_name}...")
            trainer.train_model(X_train, y_train)

            # Make predictions
            y_pred = trainer.pipeline.predict(X_test)
            y_pred_proba = (
                trainer.pipeline.predict_proba(X_test)[:, 1]
                if hasattr(trainer.pipeline, "predict_proba")
                else None
            )

            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average="weighted")
            recall = recall_score(y_test, y_pred, average="weighted")
            f1 = f1_score(y_test, y_pred, average="weighted")
            roc_auc = (
                roc_auc_score(y_test, y_pred_proba)
                if y_pred_proba is not None
                else roc_auc_score(y_test, y_pred)
            )

            # Log metrics
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("f1_score", f1)
            mlflow.log_metric("roc_auc", roc_auc)

            logger.info(
                f"Metrics - Accuracy: {accuracy:.4f}, ROC-AUC: {roc_auc:.4f}, F1: {f1:.4f}"
            )

            # Log classification report
            class_report = classification_report(y_test, y_pred, output_dict=True)
            mlflow.log_dict(class_report, "classification_report.json")

            # Log model (workaround for Dagshub - use artifact logging)
            input_example = X_train.head(1)
            try:
                # Try standard log_model first
                mlflow.sklearn.log_model(
                    trainer.pipeline,
                    "model",
                    input_example=input_example,
                )
            except Exception as e:
                # Dagshub doesn't support logged_model endpoint, use artifact logging instead
                logger.warning(
                    f"Standard model logging failed (Dagshub limitation): {str(e)}"
                )
                logger.info("Using artifact-based model logging instead...")
                import tempfile
                import shutil

                # Save model to temp directory and log as artifact
                with tempfile.TemporaryDirectory() as tmpdir:
                    model_path = os.path.join(tmpdir, "model")
                    mlflow.sklearn.save_model(
                        trainer.pipeline, model_path, input_example=input_example
                    )
                    mlflow.log_artifacts(model_path, "model")
                logger.info("Model logged as artifact successfully")

            # Save model locally as well
            trainer.save_model()
            logger.info(f"Model saved to {trainer.model_path}")

            # Step II-4: Model Registration (MLflow Model Registry)
            model_uri = f"runs:/{run.info.run_id}/model"
            model_name = "insurance_model"

            try:
                # Register model in MLflow Model Registry
                logger.info(f"Registering model: {model_name} from {model_uri}")
                model_version = mlflow.register_model(model_uri, model_name)
                logger.info(
                    f"✅ Model registered: {model_name} v{model_version.version}"
                )

                # Transition to Staging stage
                client = mlflow.tracking.MlflowClient()
                client.transition_model_version_stage(
                    name=model_name, version=model_version.version, stage="Staging"
                )
                logger.info(
                    f"✅ Model {model_name} v{model_version.version} transitioned to Staging"
                )

                # Log model registry info as tags
                mlflow.set_tag("model_registered", "true")
                mlflow.set_tag("model_version", str(model_version.version))
                mlflow.set_tag("model_stage", "Staging")

            except Exception as e:
                # Dagshub may not support model registry - log warning but continue
                logger.warning(
                    f"Model registration failed (Dagshub limitation): {str(e)}"
                )
                logger.info(
                    f"Model artifact logged at: {model_uri}. View in Dagshub MLflow UI."
                )
                mlflow.set_tag("model_registered", "false")
                mlflow.set_tag(
                    "registration_error", str(e)[:100]
                )  # Truncate long errors

            logger.info(f"✅ Training completed. Run ID: {run.info.run_id}")
            logger.info(f"Model URI: {model_uri}")

            return model_uri

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    # For local testing
    print("Starting model training with MLflow...")
    try:
        result = train_model()
        print(f"✅ Success! Model URI: {result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
