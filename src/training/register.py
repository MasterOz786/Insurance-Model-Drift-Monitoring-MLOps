"""
Model Registration Module
Registers trained models in MLflow Model Registry
"""

import mlflow
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_model(model_uri: str, model_name: str, stage: str = "Staging") -> str:
    """
    Register a model in MLflow Model Registry

    Args:
        model_uri: URI of the model (e.g., "runs:/run_id/model")
        model_name: Name for the registered model
        stage: Stage to register to (Staging, Production, Archived)

    Returns:
        str: Model version
    """
    try:
        mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        if mlflow_tracking_uri:
            mlflow.set_tracking_uri(mlflow_tracking_uri)

        logger.info(f"Registering model: {model_name} from {model_uri}")

        # Register model
        model_version = mlflow.register_model(model_uri, model_name)

        # Transition to stage
        if stage:
            client = mlflow.tracking.MlflowClient()
            client.transition_model_version_stage(
                name=model_name, version=model_version.version, stage=stage
            )
            logger.info(
                f"Model {model_name} v{model_version.version} transitioned to {stage}"
            )

        return model_version.version

    except Exception as e:
        logger.error(f"Failed to register model: {str(e)}")
        raise


if __name__ == "__main__":
    # For testing
    import sys

    if len(sys.argv) >= 3:
        register_model(sys.argv[1], sys.argv[2])
    else:
        print("Usage: register.py <model_uri> <model_name> [stage]")
