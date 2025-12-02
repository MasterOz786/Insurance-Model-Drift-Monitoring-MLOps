# Phase II — Experimentation & Model Management (MLflow on Dagshub + DVC)

## Overview
This phase sets up MLflow tracking on Dagshub for experiment tracking and model registry, along with DVC for data versioning.

---

## Prerequisites
- ✅ DVC already configured with Dagshub remote: `https://dagshub.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps`
- ✅ Dagshub account and repository created
- ✅ Dagshub access token (Settings → Access Tokens)

---

## Step 1: Configure MLflow with Dagshub

### 1.1 Get Your Dagshub Credentials
1. Go to https://dagshub.com
2. Navigate to your repository: `MasterOz786/Insurance-Model-Drift-Monitoring-MLOps`
3. Go to **Settings** → **Access Tokens**
4. Create a new token (or use existing one)
5. Copy the token

### 1.2 Add MLflow Configuration to .env
```bash
# Add to your .env file
echo "" >> .env
echo "# MLflow & Dagshub Configuration" >> .env
echo "MLFLOW_TRACKING_URI=https://dagshub.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps.mlflow" >> .env
echo "MLFLOW_USERNAME=MasterOz786" >> .env
echo "MLFLOW_PASSWORD=your_dagshub_token_here" >> .env
```

**Or manually edit `.env` and add:**
```
MLFLOW_TRACKING_URI=https://dagshub.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps.mlflow
MLFLOW_USERNAME=MasterOz786
MLFLOW_PASSWORD=your_dagshub_token_here
```

### 1.3 Verify Configuration
```bash
# Check .env file
cat .env | grep MLFLOW

# Test MLflow connection (optional)
python -c "import mlflow; import os; from dotenv import load_dotenv; load_dotenv(); mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI')); print('✅ MLflow configured:', mlflow.get_tracking_uri())"
```

---

## Step 2: Update Training Script for MLflow Integration

### 2.1 Create MLflow-Enabled Training Function

The training script needs to:
- Load data from processed pipeline
- Log parameters, metrics, and artifacts to MLflow
- Register models in MLflow Model Registry

### 2.2 Update `src/training/train.py`

We'll create a new function that integrates MLflow. The script should:
1. Load processed data from `data/processed/latest.csv`
2. Split into train/test
3. Train model with MLflow tracking
4. Log metrics and parameters
5. Save and register model

---

## Step 3: Run Training with MLflow

### 3.1 Prepare Data
```bash
# Ensure you have processed data
ls -lh data/processed/latest.csv

# If not, run the data pipeline first:
python src/data/ingestion.py
python src/data/quality_check.py
python src/data/transformation.py
```

### 3.2 Run Training
```bash
# Run training with MLflow tracking
python src/training/train.py
```

**Expected Output:**
- MLflow experiment created
- Parameters logged (model type, hyperparameters)
- Metrics logged (accuracy, precision, recall, ROC-AUC)
- Model artifact saved
- Model registered in MLflow Model Registry

---

## Step 4: View Results in Dagshub

### 4.1 Access MLflow UI on Dagshub
1. Go to: `https://dagshub.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps`
2. Click on **"Experiments"** tab (or navigate to MLflow UI)
3. You should see:
   - Experiment runs
   - Metrics and parameters
   - Model artifacts
   - Model registry

### 4.2 Check Model Registry
1. In Dagshub, go to **"Models"** or **"MLflow"** section
2. You should see registered models:
   - Model name: `insurance_model`
   - Versions
   - Stages (Staging, Production, Archived)

---

## Step 5: Version Data with DVC

### 5.1 Add Processed Data to DVC
```bash
# Add processed data to DVC tracking
dvc add data/processed/latest.csv

# Check what was created
ls -la data/processed/latest.csv.dvc
cat data/processed/latest.csv.dvc
```

### 5.2 Commit DVC Metadata to Git
```bash
# Add DVC files to Git
git add data/processed/latest.csv.dvc data/processed/.gitignore

# Commit
git commit -m "Phase II: Add processed data versioning with DVC"
```

### 5.3 Push Data to Dagshub
```bash
# Push data to DVC remote (Dagshub)
dvc push

# Verify in Dagshub UI
# Go to your repo → DVC tab → Check data files
```

---

## Step 6: Run Multiple Experiments

### 6.1 Test Different Models
Update `config.yml` to test different models:

```yaml
model:
  name: RandomForestClassifier  # Try: DecisionTreeClassifier, GradientBoostingClassifier
  params:
    n_estimators: 100
    max_depth: 10
    random_state: 42
```

### 6.2 Run Experiments
```bash
# Run multiple experiments with different configs
python src/training/train.py

# Each run will be tracked in MLflow
# Compare results in Dagshub MLflow UI
```

### 6.3 Compare Experiments
In Dagshub MLflow UI:
- Compare metrics across runs
- Identify best performing model
- Promote best model to Production stage

---

## Step 7: Model Registration and Promotion

### 7.1 Register Model (if not auto-registered)
```bash
# Get run ID from MLflow UI, then:
python src/training/register.py runs:/<run_id>/model insurance_model Production
```

### 7.2 Promote Model to Production
```python
# Or use Python:
from src.training.register import register_model
register_model("runs:/<run_id>/model", "insurance_model", "Production")
```

### 7.3 Verify in Model Registry
- Check Dagshub → Models → insurance_model
- Verify version and stage
- Model should be ready for serving

---

## Step 8: Integration with Airflow DAG

### 8.1 Update Airflow DAG
The DAG should automatically:
1. Train model with MLflow tracking
2. Register model in MLflow
3. Version data with DVC

### 8.2 Verify DAG Tasks
```bash
# Check DAG file
cat airflow/dags/ml_pipeline_dag.py | grep -A 5 "train_model\|register_model"
```

---

## Verification Checklist

### ✅ MLflow Setup
- [ ] MLflow tracking URI configured in `.env`
- [ ] Can connect to Dagshub MLflow
- [ ] Experiments visible in Dagshub UI

### ✅ Training Integration
- [ ] Training script logs to MLflow
- [ ] Parameters logged correctly
- [ ] Metrics logged correctly
- [ ] Model artifacts saved

### ✅ Model Registry
- [ ] Models registered in MLflow
- [ ] Model versions tracked
- [ ] Can promote models to Production

### ✅ DVC Integration
- [ ] Processed data tracked with DVC
- [ ] DVC metadata in Git
- [ ] Data pushed to Dagshub
- [ ] Can pull data with `dvc pull`

### ✅ Experimentation
- [ ] Multiple experiments run
- [ ] Can compare experiments
- [ ] Best model identified and promoted

---

## Troubleshooting

### Issue: Cannot connect to Dagshub MLflow
**Solution:**
```bash
# Verify credentials
cat .env | grep MLFLOW

# Test connection
python -c "import mlflow; import os; from dotenv import load_dotenv; load_dotenv(); mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI')); print(mlflow.get_tracking_uri())"
```

### Issue: DVC push fails
**Solution:**
```bash
# Check remote configuration
dvc remote list

# Verify credentials
dvc remote modify origin --local user MasterOz786
dvc remote modify origin --local password your_token

# Try push again
dvc push
```

### Issue: Model not appearing in registry
**Solution:**
- Check MLflow run completed successfully
- Verify model registration code executed
- Check Dagshub UI → Models section
- Manually register if needed: `python src/training/register.py <model_uri> insurance_model`

---

## Next Steps

After completing Phase II:
1. ✅ Models tracked in MLflow
2. ✅ Data versioned with DVC
3. ✅ Experiments reproducible
4. ✅ Best models in Production
5. → **Phase III**: Model Serving & Monitoring

---

## Quick Reference Commands

```bash
# Run training with MLflow
python src/training/train.py

# View MLflow UI locally (if needed)
mlflow ui --port 5000

# Add data to DVC
dvc add data/processed/latest.csv

# Push to Dagshub
dvc push

# Pull data from Dagshub
dvc pull

# Check MLflow experiments
# Visit: https://dagshub.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps
```

