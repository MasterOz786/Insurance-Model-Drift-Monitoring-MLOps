"""
Model Comparison Script for CML
Compares staging model vs production model and generates CML report
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
    print("❌ MLFLOW_TRACKING_URI not set. Please set it in .env or environment.")
    sys.exit(1)

if mlflow_username and mlflow_password:
    os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_username
    os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_password

mlflow.set_tracking_uri(mlflow_tracking_uri)
print(f"✅ MLflow tracking URI: {mlflow_tracking_uri}")

model_name = os.getenv("MODEL_NAME", "insurance_model")
client = MlflowClient()

try:
    # Try to get latest production model
    try:
        prod_models = client.get_latest_versions(model_name, stages=["Production"])
    except Exception as e:
        print(f"⚠️  Could not get production models: {str(e)}")
        prod_models = []

    if not prod_models:
        print("⚠️  No production model found. Will compare staging with latest run.")
        # Get latest staging model as baseline
        try:
            staging_models = client.get_latest_versions(model_name, stages=["Staging"])
            if staging_models:
                # Use oldest staging as baseline
                prod_model = staging_models[-1]  # Last one (oldest)
                prod_run = client.get_run(prod_model.run_id)
                prod_metrics = prod_run.data.metrics
                print(f"📊 Using staging model v{prod_model.version} as baseline")
            else:
                print(
                    "❌ No models found in registry. Please train and register a model first."
                )
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            sys.exit(1)
    else:
        prod_model = prod_models[0]
        prod_run = client.get_run(prod_model.run_id)
        prod_metrics = prod_run.data.metrics
        print(f"📊 Production model: v{prod_model.version}")

    # Get latest staging model
    try:
        staging_models = client.get_latest_versions(model_name, stages=["Staging"])
    except Exception as e:
        print(f"⚠️  Could not get staging models: {str(e)}")
        staging_models = []

    if not staging_models:
        print("❌ No staging model found. Please train and register a model first.")
        sys.exit(1)

    # Get the newest staging model (first in list)
    staging_model = staging_models[0]
    staging_run = client.get_run(staging_model.run_id)
    staging_metrics = staging_run.data.metrics
    print(f"📊 Staging model: v{staging_model.version}")

    # Check if comparing same model
    same_model = (
        prod_model.version == staging_model.version
        or prod_model.run_id == staging_model.run_id
    )
    if same_model:
        print(
            "⚠️  Warning: Comparing the same model version. This comparison may not be meaningful."
        )

    # Compare metrics
    metrics_to_compare = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]

    # Generate CML report
    report = f"""# Model Performance Comparison

## Model Versions
- **Production**: v{prod_model.version} (Run: {prod_model.run_id[:8]})
- **Staging**: v{staging_model.version} (Run: {staging_model.run_id[:8]})

## Metrics Comparison

| Metric | Production | Staging | Change | Status |
|--------|-----------|---------|--------|--------|
"""

    all_improved = True
    any_degraded = False
    tolerance = 1e-6  # Small tolerance for floating point comparison

    for metric in metrics_to_compare:
        prod_val = prod_metrics.get(metric, 0)
        staging_val = staging_metrics.get(metric, 0)
        change = staging_val - prod_val
        change_pct = (change / prod_val * 100) if prod_val > 0 else 0

        # Determine if improvement (higher is better for these metrics)
        # Consider equal metrics as "no change" not degraded
        if abs(change) < tolerance:
            improved = True  # No change is acceptable
            status = "➡️  No Change"
        elif change > 0:
            improved = True
            status = "✅ Improved"
        else:
            improved = False
            any_degraded = True
            status = "❌ Degraded"

        if not improved and abs(change) >= tolerance:
            all_improved = False

        sign = "+" if change >= 0 else ""

        report += f"| {metric} | {prod_val:.4f} | {staging_val:.4f} | {sign}{change:.4f} ({sign}{change_pct:.2f}%) | {status} |\n"

    # Determine recommendation
    if same_model:
        recommendation = "⚠️  **SAME MODEL**: Comparing identical model versions. No promotion needed."
    elif all_improved and not any_degraded:
        recommendation = (
            "✅ **APPROVE**: Staging model shows improvement. Ready for production."
        )
    elif any_degraded:
        recommendation = "❌ **REJECT**: Staging model performance degraded. Do not promote to production."
    else:
        recommendation = (
            "➡️  **NO CHANGE**: Staging model performance is equivalent to production."
        )

    report += f"""
## Recommendation

{recommendation}

## Model Details

### Production Model
- Version: {prod_model.version}
- Stage: {prod_model.current_stage}
- Registered: {prod_model.creation_timestamp}

### Staging Model  
- Version: {staging_model.version}
- Stage: {staging_model.current_stage}
- Registered: {staging_model.creation_timestamp}
"""

    # Write report
    with open("cml_report.md", "w") as f:
        f.write(report)

    print("✅ Model comparison complete. Report saved to cml_report.md")
    if same_model:
        print("\nSummary: ⚠️  Same model version - no comparison needed")
    elif all_improved and not any_degraded:
        print("\nSummary: ✅ Staging model is better or equal")
    elif any_degraded:
        print("\nSummary: ❌ Staging model is worse")
    else:
        print("\nSummary: ➡️  No significant change")

    # Exit with error if model degraded (but not if same model)
    if any_degraded and not same_model:
        sys.exit(1)

except Exception as e:
    print(f"❌ Error comparing models: {str(e)}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
