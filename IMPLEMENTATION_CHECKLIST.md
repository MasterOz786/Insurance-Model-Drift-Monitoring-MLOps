# Implementation Checklist - Quick Reference

Use this checklist to track your progress through the MLOps case study.

## Phase I: Problem Definition and Data Ingestion

### Step 1: Select Predictive Challenge
- [ ] Choose domain (Financial/Environmental/Logistics)
- [ ] Select API provider
- [ ] Obtain API key
- [ ] Test API connection
- [ ] **Screenshot**: API documentation and key management

### Step 2: Data Extraction (2.1)
- [ ] Implement `src/data/ingestion.py`
- [ ] Add API key to `.env`
- [ ] Test data extraction
- [ ] Verify data saved with timestamp
- [ ] **Screenshot**: Extraction code and output

### Step 2.1: Data Quality Check (Mandatory Gate)
- [ ] Verify `src/data/quality_check.py` works
- [ ] Test with good data (should pass)
- [ ] Test with bad data (should fail)
- [ ] Verify DAG fails on quality check failure
- [ ] **Screenshot**: Quality check passing and failing

### Step 2.2: Data Transformation
- [ ] Update `src/data/transformation.py`
- [ ] Add time-series features (lags, rolling stats)
- [ ] Create target variable
- [ ] Save processed data
- [ ] **Screenshot**: Transformation code and before/after data

### Step 2.3: Data Profiling
- [ ] Run profiling script
- [ ] Generate HTML report
- [ ] Review report content
- [ ] **Screenshot**: Profiling report in browser

### Step 2.4: Storage & Versioning
- [ ] Set up MinIO/S3
- [ ] Configure storage in `.env`
- [ ] Test `src/data/storage.py`
- [ ] Verify data uploaded
- [ ] **Screenshot**: Storage console with uploaded files

### Step 3: DVC Versioning
- [ ] Initialize DVC (if needed)
- [ ] Configure DVC remote (Dagshub/S3)
- [ ] Add data with `dvc add`
- [ ] Commit `.dvc` file
- [ ] Push data with `dvc push`
- [ ] **Screenshot**: DVC files in Git and remote storage

---

## Phase II: Experimentation and Model Management

### Step 4: Dagshub Setup
- [ ] Create Dagshub account
- [ ] Create repository
- [ ] Configure MLflow tracking URI
- [ ] Configure DVC remote
- [ ] Test connection
- [ ] **Screenshot**: Dagshub repository and configuration

### Step 5: MLflow Integration
- [ ] Update `src/training/train.py` with MLflow
- [ ] Log parameters
- [ ] Log metrics (RMSE, MAE, R²)
- [ ] Log model artifact
- [ ] Register model
- [ ] **Screenshot**: MLflow experiment run and model registry

### Step 6: Model Registration
- [ ] Verify `src/training/register.py` works
- [ ] Register model in registry
- [ ] Transition model stages
- [ ] **Screenshot**: Model versions and stages

---

## Phase III: CI/CD

### Step 7: Git Branching
- [ ] Create dev, test, master branches
- [ ] Set up branch protection
- [ ] Require PR approvals
- [ ] **Screenshot**: Branch structure and protection rules

### Step 8: CI - Feature → Dev
- [ ] Verify `.github/workflows/ci-dev.yml`
- [ ] Create feature branch
- [ ] Create PR to dev
- [ ] Verify workflow runs
- [ ] Check linting passes
- [ ] Check tests pass
- [ ] **Screenshot**: Workflow run and PR checks

### Step 9: CI - Dev → Test (with CML)
- [ ] Create `scripts/compare_models.py`
- [ ] Add GitHub Secrets (MLflow credentials)
- [ ] Create PR to test
- [ ] Verify model retraining
- [ ] Verify CML report in PR
- [ ] **Screenshot**: CML report in PR comments

### Step 10: CD - Test → Master
- [ ] Add Docker Hub secrets
- [ ] Create `scripts/get_best_model.py`
- [ ] Merge to master
- [ ] Verify Docker build
- [ ] Verify image push
- [ ] **Screenshot**: Docker build logs and registry

### Step 11: Docker Containerization
- [ ] Verify `docker/Dockerfile.api`
- [ ] Build Docker image
- [ ] Run container
- [ ] Test health check
- [ ] **Screenshot**: Docker build and running container

### Step 12: Docker Compose
- [ ] Verify `docker/docker-compose.yml`
- [ ] Start all services
- [ ] Verify services running
- [ ] **Screenshot**: All services running

---

## Phase IV: Monitoring

### Step 13: Prometheus Integration
- [ ] Verify `src/serving/prometheus.py`
- [ ] Start API
- [ ] Check `/metrics` endpoint
- [ ] Verify metrics format
- [ ] **Screenshot**: Metrics endpoint output

### Step 14: Prometheus Configuration
- [ ] Verify `docker/prometheus/prometheus.yml`
- [ ] Start Prometheus
- [ ] Verify targets UP
- [ ] Query metrics
- [ ] **Screenshot**: Prometheus UI and targets

### Step 15: Grafana Dashboard
- [ ] Start Grafana
- [ ] Add Prometheus data source
- [ ] Create dashboard
- [ ] Add panels (request count, latency, drift)
- [ ] **Screenshot**: Dashboard with all panels

### Step 16: Grafana Alerts
- [ ] Create alert rules
- [ ] Configure notification channel
- [ ] Test alert (if possible)
- [ ] **Screenshot**: Alert configuration and notification

---

## Final Deliverables

### Documentation
- [ ] Updated README.md
- [ ] Architecture diagram
- [ ] API documentation
- [ ] Deployment guide

### Code
- [ ] All source code committed
- [ ] Airflow DAG working
- [ ] CI/CD workflows functional
- [ ] Docker containers buildable

### Screenshots
- [ ] Phase I: 7+ screenshots
- [ ] Phase II: 4+ screenshots
- [ ] Phase III: 8+ screenshots
- [ ] Phase IV: 5+ screenshots
- [ ] Total: 24+ screenshots

### Testing
- [ ] End-to-end pipeline test
- [ ] Model training test
- [ ] API serving test
- [ ] Monitoring test

---

## Quick Commands Reference

```bash
# Data Pipeline
python src/data/ingestion.py
python src/data/quality_check.py
python src/data/transformation.py

# Training
export MLFLOW_TRACKING_URI=https://dagshub.com/user/repo.mlflow
python src/training/train.py

# API
uvicorn src.serving.api:app --reload

# Docker
docker-compose -f docker/docker-compose.yml up -d

# DVC
dvc add data/processed/latest.csv
dvc push

# Git
git checkout -b feature/new-feature
```

---

## Screenshot Checklist

### Must-Have Screenshots:
1. ✅ API selection/configuration
2. ✅ Data extraction working
3. ✅ Quality check (pass/fail)
4. ✅ Data profiling report
5. ✅ DVC versioning
6. ✅ Dagshub repository
7. ✅ MLflow experiment run
8. ✅ Model registry
9. ✅ GitHub branch structure
10. ✅ CI workflow runs (all 3)
11. ✅ CML report in PR
12. ✅ Docker build/push
13. ✅ Prometheus targets
14. ✅ Grafana dashboard
15. ✅ Alert configuration

---

**Progress Tracker**: Update this checklist as you complete each item!

