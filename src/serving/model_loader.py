"""
Model Loader Module
Loads models from MLflow Model Registry
"""

import mlflow
import mlflow.sklearn
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model_from_mlflow(model_name: str, stage: str = "Production") -> tuple:
    """
    Load model from MLflow Model Registry
    
    Args:
        model_name: Name of the registered model
        stage: Model stage (Production, Staging, Archived)
    
    Returns:
        tuple: (model, model_version)
    """
    try:
        # Construct model URI
        model_uri = f"models:/{model_name}/{stage}"
        
        logger.info(f"Loading model from MLflow: {model_uri}")
        
        # Load model
        model = mlflow.sklearn.load_model(model_uri)
        
        # Get model version info
        client = mlflow.tracking.MlflowClient()
        latest_version = client.get_latest_versions(model_name, stages=[stage])
        
        if latest_version:
            model_version = latest_version[0].version
        else:
            model_version = "unknown"
        
        logger.info(f"Model loaded successfully: {model_name} v{model_version}")
        
        return model, model_version
        
    except Exception as e:
        logger.error(f"Failed to load model from MLflow: {str(e)}")
        raise


def load_model_from_local(path: str):
    """Fallback: Load model from local file"""
    import joblib
    logger.info(f"Loading model from local path: {path}")
    return joblib.load(path), "local"

