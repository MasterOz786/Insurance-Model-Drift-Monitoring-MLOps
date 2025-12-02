"""
FastAPI Application with Prometheus Metrics and Model Serving
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import mlflow
import os
import logging
import time
from typing import Dict, Any

from .prometheus import (
    get_metrics,
    track_prediction,
    track_data_drift,
    PrometheusMiddleware
)
from .model_loader import load_model_from_mlflow
from ..monitoring.drift_detection import check_feature_drift

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Insurance Model API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)

# Load model at startup
model = None
model_version = None

@app.on_event("startup")
async def startup_event():
    """Load model from MLflow on startup"""
    global model, model_version
    try:
        mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
        model_name = os.getenv('MODEL_NAME', 'insurance_model')
        stage = os.getenv('MODEL_STAGE', 'Production')
        
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        model, model_version = load_model_from_mlflow(model_name, stage)
        logger.info(f"Model loaded successfully: {model_name} (version: {model_version})")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise


class InputData(BaseModel):
    Gender: str
    Age: int
    HasDrivingLicense: int
    RegionID: float
    Switch: int
    PastAccident: str
    AnnualPremium: float


@app.get("/")
async def read_root():
    """Root endpoint"""
    return {
        "service": "Insurance Model API",
        "status": "running",
        "model_version": model_version
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_version": model_version
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return get_metrics()


@app.post("/predict")
async def predict(input_data: InputData):
    """
    Prediction endpoint with drift detection and metrics tracking
    """
    start_time = time.time()
    
    try:
        # Convert input to DataFrame
        input_dict = input_data.model_dump()
        df = pd.DataFrame([input_dict.values()], columns=input_dict.keys())
        
        # Check for data drift
        drift_results = {}
        for feature in ['AnnualPremium', 'Age', 'RegionID']:
            if feature in df.columns:
                is_drift = check_feature_drift(feature, df[feature].iloc[0])
                drift_results[feature] = is_drift
                track_data_drift(feature, is_drift)
        
        # Make prediction
        prediction = model.predict(df)
        prediction_proba = model.predict_proba(df) if hasattr(model, 'predict_proba') else None
        
        # Track prediction metrics
        duration = time.time() - start_time
        track_prediction(str(model_version), duration, 'success')
        
        result = {
            "predicted_class": int(prediction[0]),
            "model_version": model_version,
            "drift_detected": any(drift_results.values()),
            "drift_details": drift_results
        }
        
        if prediction_proba is not None:
            result["prediction_probability"] = float(prediction_proba[0][prediction[0]])
        
        return result
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        duration = time.time() - start_time
        track_prediction(str(model_version), duration, 'error')
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
