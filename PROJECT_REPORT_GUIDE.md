# MLOps Case Study: Real-Time Predictive System (RPS)
## Complete Step-by-Step Implementation Guide

This guide provides detailed steps for implementing all requirements of the MLOps case study, including what to document and screenshot.

---

## 📋 Table of Contents

1. [Phase I: Problem Definition and Data Ingestion](#phase-i-problem-definition-and-data-ingestion)
2. [Phase II: Experimentation and Model Management](#phase-ii-experimentation-and-model-management)
3. [Phase III: Continuous Integration & Deployment (CI/CD)](#phase-iii-continuous-integration--deployment-cicd)
4. [Phase IV: Monitoring and Observability](#phase-iv-monitoring-and-observability)
5. [Final Deliverables Checklist](#final-deliverables-checklist)

---

## Phase I: Problem Definition and Data Ingestion

### Step 1: Select Predictive Challenge

#### 1.1 Choose Your Domain and API

**Options:**
- **Financial**: Alpha Vantage, Twelve Data (Stock/Crypto volatility prediction)
- **Environmental**: OpenWeatherMap (Weather forecasting)
- **Logistics**: Public Transit Data (ETA/Delay prediction)

**Action Items:**
1. Research and select one API
2. Sign up and obtain API key
3. Test API connection

**Screenshots to Take:**
- ✅ API documentation page showing available endpoints
- ✅ API key generation/management page
- ✅ Successful API test response (JSON/XML output)

**Documentation:**
```markdown
### Selected Domain: [Your Choice]
- **API Provider**: [Name]
- **API Endpoint**: [URL]
- **Predictive Task**: [Description]
- **API Key**: [Stored in .env, not in documentation]
```

---

### Step 2: Implement Data Extraction (2.1)

#### 2.1.1 Update Ingestion Module

**File**: `src/data/ingestion.py`

**Implementation Steps:**

1. **Install required packages:**
   ```bash
   pip install requests python-dotenv
   ```

2. **Create API ingestion function:**
   ```python
   import requests
   import pandas as pd
   import os
   from datetime import datetime
   from dotenv import load_dotenv
   
   load_dotenv()
   
   def extract_data(**context):
       """
       Extract data from external API
       Example for Alpha Vantage (Financial)
       """
       api_key = os.getenv('API_KEY')
       symbol = os.getenv('SYMBOL', 'AAPL')  # Default stock symbol
       
       url = f'https://www.alphavantage.co/query'
       params = {
           'function': 'TIME_SERIES_INTRADAY',
           'symbol': symbol,
           'interval': '60min',
           'apikey': api_key
       }
       
       response = requests.get(url, params=params)
       data = response.json()
       
       # Convert to DataFrame
       time_series = data.get('Time Series (60min)', {})
       df = pd.DataFrame.from_dict(time_series, orient='index')
       df.index = pd.to_datetime(df.index)
       df = df.astype(float)
       
       # Add collection timestamp
       df['collection_timestamp'] = datetime.now()
       
       # Save raw data
       os.makedirs('data/raw', exist_ok=True)
       timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
       output_path = f'data/raw/latest_extract_{timestamp}.csv'
       df.to_csv(output_path)
       
       # Also save as latest for quality check
       df.to_csv('data/raw/latest_extract.csv')
       
       return output_path
   ```

3. **Create `.env` file** (not committed):
   ```bash
   API_KEY=your_api_key_here
   SYMBOL=AAPL
   ```

**Testing:**
```bash
python -c "from src.data.ingestion import extract_data; extract_data()"
```

**Screenshots to Take:**
- ✅ Code implementation in `src/data/ingestion.py`
- ✅ Successful data extraction output (terminal/logs)
- ✅ Raw data file in `data/raw/` directory
- ✅ Sample of extracted data (first few rows)

**Verification:**
- [ ] Data file created in `data/raw/`
- [ ] Data contains timestamp column
- [ ] Data format is correct (CSV)

---

#### 2.1.2 Implement Data Quality Check (Mandatory Quality Gate)

**File**: `src/data/quality_check.py` (Already created, verify it works)

**Testing:**
```bash
python src/data/quality_check.py
```

**Screenshots to Take:**
- ✅ Quality check code implementation
- ✅ Quality check passing (terminal output showing "✅ All quality checks passed!")
- ✅ Quality check failing scenario (if you can demonstrate - modify data to fail)
- ✅ Airflow DAG showing quality check task

**Verification:**
- [ ] Quality check validates null values (< 1%)
- [ ] Quality check validates schema
- [ ] Quality check validates data volume
- [ ] DAG fails if quality check fails

---

### Step 3: Data Transformation (2.2)

#### 3.1 Update Transformation Module

**File**: `src/data/transformation.py` (Update existing)

**Implementation Steps:**

1. **Add time-series specific feature engineering:**
   ```python
   def transform_data(**context):
       """
       Transform raw data with time-series features
       """
       import pandas as pd
       import numpy as np
       
       # Load raw data
       df = pd.read_csv('data/raw/latest_extract.csv', index_col=0, parse_dates=True)
       
       # Time-series feature engineering
       df['hour'] = df.index.hour
       df['day_of_week'] = df.index.dayofweek
       df['lag_1'] = df['close'].shift(1)  # Previous hour's close
       df['lag_2'] = df['close'].shift(2)
       df['rolling_mean_3'] = df['close'].rolling(window=3).mean()
       df['rolling_std_3'] = df['close'].rolling(window=3).std()
       
       # Target variable (next hour's volatility or price)
       df['target'] = df['close'].shift(-1)  # Predict next hour
       
       # Drop NaN rows
       df = df.dropna()
       
       # Save processed data
       os.makedirs('data/processed', exist_ok=True)
       df.to_csv('data/processed/latest.csv')
       
       return 'data/processed/latest.csv'
   ```

**Screenshots to Take:**
- ✅ Transformation code showing feature engineering
- ✅ Before/after data comparison (raw vs processed)
- ✅ Feature statistics (describe() output)
- ✅ Processed data file location

**Verification:**
- [ ] Lag features created
- [ ] Rolling statistics calculated
- [ ] Target variable created
- [ ] Data saved to `data/processed/`

---

#### 3.2 Generate Data Profiling Report

**File**: `src/data/profiling.py` (Already created)

**Testing:**
```bash
python src/data/profiling.py data/processed/latest.csv data/reports/profile.html
```

**Screenshots to Take:**
- ✅ Profiling report generation command
- ✅ Generated HTML report (screenshot of report in browser)
- ✅ Report showing data statistics, distributions, correlations
- ✅ Report saved to MLflow (if integrated)

**Verification:**
- [ ] Report generated successfully
- [ ] Report contains key statistics
- [ ] Report logged to MLflow (optional but recommended)

---

### Step 4: Data Loading & Versioning (2.3 & 3)

#### 4.1 Save to Cloud Storage

**File**: `src/data/storage.py` (Already created, configure it)

**Implementation Steps:**

1. **For Local Development (MinIO):**
   ```bash
   # Install MinIO client or use Docker
   docker run -d -p 9000:9000 -p 9001:9001 \
     --name minio \
     -e "MINIO_ROOT_USER=minioadmin" \
     -e "MINIO_ROOT_PASSWORD=minioadmin" \
     minio/minio server /data --console-address ":9001"
   ```

2. **Update `.env`:**
   ```bash
   STORAGE_TYPE=minio
   S3_ENDPOINT_URL=http://localhost:9000
   AWS_ACCESS_KEY_ID=minioadmin
   AWS_SECRET_ACCESS_KEY=minioadmin
   STORAGE_BUCKET=mlops-data
   ```

3. **Test storage:**
   ```bash
   python src/data/storage.py
   ```

**Screenshots to Take:**
- ✅ MinIO/S3 console showing uploaded files
- ✅ Storage configuration in code
- ✅ Successful upload confirmation
- ✅ File listing in storage bucket

**Verification:**
- [ ] Data uploaded to storage
- [ ] File accessible via storage interface
- [ ] Timestamped file names

---

#### 4.2 Version Data with DVC

**Implementation Steps:**

1. **Initialize DVC (if not done):**
   ```bash
   dvc init
   ```

2. **Configure DVC remote (Dagshub or S3):**
   ```bash
   # For Dagshub
   dvc remote add origin https://dagshub.com/username/repo.dvc
   dvc remote modify origin --local auth basic
   dvc remote modify origin --local user your_username
   dvc remote modify origin --local password your_token
   ```

3. **Add and push data:**
   ```bash
   dvc add data/processed/latest.csv
   git add data/processed/latest.csv.dvc data/processed/.gitignore
   git commit -m "Add processed data"
   dvc push
   ```

**Screenshots to Take:**
- ✅ DVC initialization output
- ✅ DVC remote configuration
- ✅ `dvc add` command output
- ✅ `.dvc` file in Git (showing metadata)
- ✅ Data file in DVC remote (Dagshub/S3)
- ✅ Dagshub UI showing DVC files (if using Dagshub)

**Verification:**
- [ ] `.dvc` file created
- [ ] `.dvc` file committed to Git
- [ ] Data pushed to remote storage
- [ ] Can pull data with `dvc pull`

---

## Phase II: Experimentation and Model Management

### Step 5: MLflow & Dagshub Integration (Step 4)

#### 5.1 Set Up Dagshub

**Implementation Steps:**

1. **Create Dagshub account and repository:**
   - Go to https://dagshub.com
   - Create account
   - Create new repository

2. **Run setup script:**
   ```bash
   ./scripts/setup_dagshub.sh
   ```

3. **Or manually configure:**
   ```bash
   # MLflow tracking URI
   export MLFLOW_TRACKING_URI=https://dagshub.com/username/repo.mlflow
   
   # DVC remote
   dvc remote add origin https://dagshub.com/username/repo.dvc
   ```

**Screenshots to Take:**
- ✅ Dagshub repository creation page
- ✅ Dagshub repository dashboard
- ✅ MLflow tracking URI configuration
- ✅ DVC remote configuration
- ✅ Setup script execution

**Verification:**
- [ ] Dagshub repository created
- [ ] MLflow tracking URI set
- [ ] DVC remote configured
- [ ] Can connect to Dagshub

---

#### 5.2 Update Training Script

**File**: `src/training/train.py`

**Implementation Steps:**

1. **Update training script to use MLflow:**
   ```python
   import mlflow
   import mlflow.sklearn
   from sklearn.model_selection import train_test_split
   from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
   import os
   
   def train_model(**context):
       # Set MLflow tracking
       mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
       mlflow.set_experiment("Time Series Prediction")
       
       # Load data
       df = pd.read_csv('data/processed/latest.csv', index_col=0, parse_dates=True)
       
       # Prepare features and target
       X = df.drop('target', axis=1)
       y = df['target']
       
       X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
       
       with mlflow.start_run():
           # Log parameters
           mlflow.log_param("model_type", "RandomForestRegressor")
           mlflow.log_param("n_estimators", 100)
           mlflow.log_param("max_depth", 10)
           
           # Train model
           from sklearn.ensemble import RandomForestRegressor
           model = RandomForestRegressor(n_estimators=100, max_depth=10)
           model.fit(X_train, y_train)
           
           # Evaluate
           y_pred = model.predict(X_test)
           rmse = np.sqrt(mean_squared_error(y_test, y_pred))
           mae = mean_absolute_error(y_test, y_pred)
           r2 = r2_score(y_test, y_pred)
           
           # Log metrics
           mlflow.log_metric("rmse", rmse)
           mlflow.log_metric("mae", mae)
           mlflow.log_metric("r2_score", r2)
           
           # Log model
           mlflow.sklearn.log_model(model, "model")
           
           # Register model
           model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
           mlflow.register_model(model_uri, "time_series_model")
   ```

2. **Test training:**
   ```bash
   export MLFLOW_TRACKING_URI=https://dagshub.com/username/repo.mlflow
   python src/training/train.py
   ```

**Screenshots to Take:**
- ✅ Training script code
- ✅ Training execution (terminal output)
- ✅ MLflow experiment run in Dagshub UI
- ✅ Logged parameters in MLflow
- ✅ Logged metrics in MLflow
- ✅ Model artifact in MLflow
- ✅ Model registered in MLflow Model Registry

**Verification:**
- [ ] Model trained successfully
- [ ] Parameters logged to MLflow
- [ ] Metrics logged to MLflow
- [ ] Model artifact saved
- [ ] Model registered in registry

---

#### 5.3 Update Model Registration

**File**: `src/training/register.py` (Already created)

**Testing:**
```bash
python src/training/register.py
```

**Screenshots to Take:**
- ✅ Model registration code
- ✅ Model versions in MLflow Model Registry
- ✅ Model stage transitions (Staging → Production)
- ✅ Model metadata in registry

**Verification:**
- [ ] Model registered successfully
- [ ] Model version created
- [ ] Model stage set correctly

---

## Phase III: Continuous Integration & Deployment (CI/CD)

### Step 6: Git Workflow and Branching (5.1)

#### 6.1 Set Up Branching Strategy

**Implementation Steps:**

1. **Create branches:**
   ```bash
   git checkout -b dev
   git checkout -b test
   git checkout -b feature/api-integration
   ```

2. **Set up branch protection in GitHub:**
   - Go to Settings → Branches
   - Add rule for `test` branch:
     - Require pull request reviews (1 approval)
     - Require status checks to pass
   - Add rule for `master` branch:
     - Require pull request reviews (1 approval)
     - Require status checks to pass

**Screenshots to Take:**
- ✅ Git branch structure (git branch -a output)
- ✅ GitHub branch protection settings
- ✅ Branch protection rules configured
- ✅ PR creation workflow

**Verification:**
- [ ] Branches created: dev, test, master
- [ ] Branch protection enabled
- [ ] PR approval required

---

### Step 7: GitHub Actions CI/CD (5.1 & 5.2)

#### 7.1 Feature → Dev Workflow

**File**: `.github/workflows/ci-dev.yml` (Already created)

**Implementation Steps:**

1. **Add GitHub Secrets:**
   - Go to Settings → Secrets and variables → Actions
   - Add secrets (if needed for this workflow)

2. **Test workflow:**
   - Create feature branch
   - Make changes
   - Create PR to dev
   - Workflow should trigger

**Screenshots to Take:**
- ✅ GitHub Actions workflow file
- ✅ Workflow run in GitHub Actions tab
- ✅ Linting results
- ✅ Unit test results
- ✅ Coverage report
- ✅ PR with passing checks

**Verification:**
- [ ] Workflow triggers on PR to dev
- [ ] Linting passes
- [ ] Unit tests pass
- [ ] Coverage reported

---

#### 7.2 Dev → Test Workflow (with CML)

**File**: `.github/workflows/ci-test.yml` (Already created)

**Implementation Steps:**

1. **Install CML:**
   ```bash
   npm install -g @dvcorg/cml
   ```

2. **Create model comparison script:**
   ```python
   # scripts/compare_models.py
   import mlflow
   import os
   
   mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
   client = mlflow.tracking.MlflowClient()
   
   # Get latest production model
   prod_model = client.get_latest_versions("time_series_model", stages=["Production"])[0]
   prod_metrics = client.get_run(prod_model.run_id).data.metrics
   
   # Get latest staging model
   staging_model = client.get_latest_versions("time_series_model", stages=["Staging"])[0]
   staging_metrics = client.get_run(staging_model.run_id).data.metrics
   
   # Compare
   print(f"Production RMSE: {prod_metrics.get('rmse', 'N/A')}")
   print(f"Staging RMSE: {staging_metrics.get('rmse', 'N/A')}")
   
   # Generate CML report
   report = f"""
   # Model Performance Comparison
   
   | Metric | Production | Staging | Change |
   |--------|-----------|---------|--------|
   | RMSE   | {prod_metrics.get('rmse', 'N/A')} | {staging_metrics.get('rmse', 'N/A')} | ... |
   | MAE    | {prod_metrics.get('mae', 'N/A')} | {staging_metrics.get('mae', 'N/A')} | ... |
   | R²     | {prod_metrics.get('r2_score', 'N/A')} | {staging_metrics.get('r2_score', 'N/A')} | ... |
   """
   
   with open('cml_report.md', 'w') as f:
       f.write(report)
   ```

3. **Add GitHub Secrets:**
   - `MLFLOW_TRACKING_URI`
   - `MLFLOW_USERNAME`
   - `MLFLOW_PASSWORD`

**Screenshots to Take:**
- ✅ CML workflow file
- ✅ Workflow run executing
- ✅ Model training in workflow
- ✅ CML report in PR comments
- ✅ Model comparison table
- ✅ PR with CML report attached

**Verification:**
- [ ] Workflow triggers on PR to test
- [ ] Model retraining executes
- [ ] CML report generated
- [ ] Report posted to PR
- [ ] Merge blocked if model worse

---

#### 7.3 Test → Master Workflow (Docker Build & Deploy)

**File**: `.github/workflows/cd-master.yml` (Already created)

**Implementation Steps:**

1. **Add Docker Hub secrets:**
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`

2. **Create get_best_model script:**
   ```python
   # scripts/get_best_model.py
   import mlflow
   import os
   import sys
   
   mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
   client = mlflow.tracking.MlflowClient()
   
   model_name = os.getenv('MODEL_NAME', 'time_series_model')
   model = client.get_latest_versions(model_name, stages=["Production"])[0]
   print(model.version)
   ```

3. **Test workflow:**
   - Merge to master
   - Workflow should build and push Docker image

**Screenshots to Take:**
- ✅ CD workflow file
- ✅ Workflow run building Docker image
- ✅ Docker image build logs
- ✅ Docker image pushed to registry
- ✅ Docker Hub showing new image
- ✅ Image tags (version and latest)
- ✅ Deployment verification

**Verification:**
- [ ] Workflow triggers on merge to master
- [ ] Docker image builds successfully
- [ ] Image pushed to Docker Hub
- [ ] Image tagged correctly

---

### Step 8: Containerization (5.4 & 5.5)

#### 8.1 Update Dockerfile

**File**: `docker/Dockerfile.api` (Already created)

**Testing:**
```bash
cd docker
docker build -f Dockerfile.api -t insurance-model-api:test ..
docker run -p 8000:8000 insurance-model-api:test
```

**Screenshots to Take:**
- ✅ Dockerfile content
- ✅ Docker build command
- ✅ Build logs (successful)
- ✅ Docker image created
- ✅ Container running
- ✅ Health check endpoint response
- ✅ API docs accessible

**Verification:**
- [ ] Docker image builds
- [ ] Container starts
- [ ] Health check passes
- [ ] API responds

---

#### 8.2 Docker Compose Setup

**File**: `docker/docker-compose.yml` (Already created)

**Testing:**
```bash
cd docker
docker-compose up -d
docker-compose ps
docker-compose logs
```

**Screenshots to Take:**
- ✅ docker-compose.yml file
- ✅ All services running (docker-compose ps)
- ✅ Service logs
- ✅ Network connectivity
- ✅ All services healthy

**Verification:**
- [ ] All services start
- [ ] Services can communicate
- [ ] Ports exposed correctly

---

## Phase IV: Monitoring and Observability

### Step 9: Prometheus Integration

#### 9.1 Verify Prometheus Metrics

**File**: `src/serving/prometheus.py` (Already created)

**Testing:**
```bash
# Start API
uvicorn src.serving.api:app --reload

# In another terminal, check metrics
curl http://localhost:8000/metrics
```

**Screenshots to Take:**
- ✅ Prometheus metrics code
- ✅ `/metrics` endpoint response
- ✅ Metrics in Prometheus format
- ✅ API request metrics
- ✅ Model prediction metrics
- ✅ Data drift metrics

**Verification:**
- [ ] Metrics endpoint accessible
- [ ] Metrics in correct format
- [ ] Custom metrics exposed

---

#### 9.2 Prometheus Configuration

**File**: `docker/prometheus/prometheus.yml` (Already created)

**Testing:**
```bash
# Start Prometheus
docker-compose up prometheus

# Access Prometheus UI
open http://localhost:9090
```

**Screenshots to Take:**
- ✅ Prometheus configuration file
- ✅ Prometheus UI (targets page)
- ✅ Targets showing as "UP"
- ✅ Metrics query interface
- ✅ Sample query results

**Verification:**
- [ ] Prometheus scrapes API
- [ ] Targets healthy
- [ ] Metrics queryable

---

### Step 10: Grafana Dashboard

#### 10.1 Create Dashboard

**Implementation Steps:**

1. **Access Grafana:**
   ```bash
   docker-compose up grafana
   # Access http://localhost:3000
   # Login: admin/admin
   ```

2. **Add Prometheus Data Source:**
   - Configuration → Data Sources
   - Add Prometheus
   - URL: http://prometheus:9090
   - Save & Test

3. **Create Dashboard:**
   - Create new dashboard
   - Add panels for:
     - API request count
     - API latency
     - Model prediction count
     - Model prediction latency
     - Data drift ratio

**Screenshots to Take:**
- ✅ Grafana login page
- ✅ Prometheus data source configuration
- ✅ Data source test (successful)
- ✅ Dashboard creation
- ✅ Dashboard with all panels
- ✅ Real-time metrics visualization
- ✅ Panel configurations

**Verification:**
- [ ] Data source connected
- [ ] Dashboard created
- [ ] Panels show data
- [ ] Metrics updating in real-time

---

#### 10.2 Configure Alerts

**Implementation Steps:**

1. **Create Alert Rules:**
   - In Grafana, go to Alerting → Alert Rules
   - Create rule for:
     - Inference latency > 500ms
     - Data drift ratio > 0.1

2. **Configure Notification Channel:**
   - Add Slack or email channel
   - Test notification

**Screenshots to Take:**
- ✅ Alert rule configuration
- ✅ Alert conditions set
- ✅ Notification channel setup
- ✅ Alert firing (if you can trigger it)
- ✅ Alert notification received

**Verification:**
- [ ] Alerts configured
- [ ] Alerts fire on threshold
- [ ] Notifications sent

---

## Final Deliverables Checklist

### Documentation Required

- [ ] **README.md** - Updated with new structure
- [ ] **Architecture Diagram** - Show complete flow
- [ ] **API Documentation** - Endpoints and usage
- [ ] **Deployment Guide** - How to deploy
- [ ] **Monitoring Guide** - How to monitor

### Screenshots Portfolio

#### Phase I Screenshots:
1. API selection and configuration
2. Data extraction working
3. Quality check passing/failing
4. Data transformation results
5. Profiling report
6. Data in cloud storage
7. DVC versioning

#### Phase II Screenshots:
1. Dagshub repository
2. MLflow experiment runs
3. Model registry
4. Model versions and stages

#### Phase III Screenshots:
1. Git branching structure
2. Branch protection rules
3. CI workflow runs (3 workflows)
4. CML reports in PRs
5. Docker builds
6. Docker images in registry
7. Deployment verification

#### Phase IV Screenshots:
1. Prometheus targets
2. Prometheus metrics queries
3. Grafana dashboard
4. Alert configurations
5. Alert notifications

### Code Deliverables

- [ ] All source code in `src/`
- [ ] Airflow DAG working
- [ ] CI/CD workflows functional
- [ ] Docker containers buildable
- [ ] Monitoring integrated

### Verification Tests

- [ ] End-to-end pipeline runs
- [ ] Model trains and registers
- [ ] API serves predictions
- [ ] Metrics collected
- [ ] Alerts fire correctly

---

## 📸 Screenshot Organization Template

Create a folder structure for screenshots:

```
screenshots/
├── phase1_data_ingestion/
│   ├── 01_api_selection.png
│   ├── 02_data_extraction.png
│   ├── 03_quality_check.png
│   └── ...
├── phase2_mlflow/
│   ├── 01_dagshub_setup.png
│   ├── 02_experiment_runs.png
│   └── ...
├── phase3_cicd/
│   ├── 01_github_workflows.png
│   ├── 02_docker_build.png
│   └── ...
└── phase4_monitoring/
    ├── 01_prometheus.png
    ├── 02_grafana_dashboard.png
    └── ...
```

---

## 🎯 Quick Reference: Command Cheat Sheet

```bash
# Data Pipeline
python src/data/ingestion.py
python src/data/quality_check.py
python src/data/transformation.py
python src/data/profiling.py data/processed/latest.csv data/reports/profile.html

# Training
python src/training/train.py
python src/training/register.py

# API
uvicorn src.serving.api:app --reload

# Docker
docker-compose up -d
docker-compose logs -f

# DVC
dvc add data/processed/latest.csv
dvc push

# Git
git checkout -b feature/new-feature
git push origin feature/new-feature
```

---

## 📝 Report Structure Template

When writing your final report, use this structure:

1. **Introduction**
   - Problem statement
   - Selected domain and API
   - Objectives

2. **Architecture Overview**
   - System architecture diagram
   - Component descriptions

3. **Implementation Details**
   - Phase I: Data pipeline
   - Phase II: MLflow integration
   - Phase III: CI/CD
   - Phase IV: Monitoring

4. **Results and Screenshots**
   - Each phase with screenshots
   - Metrics and performance

5. **Challenges and Solutions**
   - Issues encountered
   - How resolved

6. **Conclusion**
   - Summary
   - Future improvements

---

**Good luck with your implementation! 🚀**

