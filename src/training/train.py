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
        if mlflow_tracking_uri:
            mlflow.set_tracking_uri(mlflow_tracking_uri)
            logger.info(f"MLflow tracking URI: {mlflow_tracking_uri}")
        else:
            # Fallback to local
            mlruns_path = os.path.abspath(os.path.join(os.getcwd(), "mlruns"))
            mlflow.set_tracking_uri(f"file://{mlruns_path}")
            logger.warning("MLFLOW_TRACKING_URI not set, using local storage")

        # Set experiment
        experiment_name = os.getenv(
            "MLFLOW_EXPERIMENT_NAME", "Insurance Model Training"
        )
        mlflow.set_experiment(experiment_name)

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

            # Log model
            input_example = X_train.head(1)
            mlflow.sklearn.log_model(
                trainer.pipeline,
                "model",
                input_example=input_example,
                registered_model_name="insurance_model",
            )

            # Save model locally as well
            trainer.save_model()
            logger.info(f"Model saved to {trainer.model_path}")

            # Register model
            model_uri = f"runs:/{run.info.run_id}/model"
            model_name = "insurance_model"

            try:
                model_version = mlflow.register_model(model_uri, model_name)
                logger.info(
                    f"✅ Model registered: {model_name} v{model_version.version}"
                )

                # Transition to Staging
                client = mlflow.tracking.MlflowClient()
                client.transition_model_version_stage(
                    name=model_name, version=model_version.version, stage="Staging"
                )
                logger.info(
                    f"Model {model_name} v{model_version.version} transitioned to Staging"
                )
            except Exception as e:
                logger.warning(
                    f"Model registration failed (may already exist): {str(e)}"
                )

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
