# Phase III — CI/CD with Dagshub + GitHub Actions

## Overview
Set up Continuous Integration and Continuous Deployment (CI/CD) pipelines using GitHub Actions and Dagshub CI to automate testing, training, and deployment.

---

## Step 1: Set Up GitHub Actions Workflows

### Step 1.1: Create GitHub Actions Directory

```bash
mkdir -p .github/workflows
```

### Step 1.2: Create CI Workflow for Feature → Dev

Create `.github/workflows/ci-dev.yml`:

This workflow will:
- Run on PRs to `dev` branch
- Lint code with Black
- Run unit tests
- Check code quality

### Step 1.3: Create CI/CD Workflow for Dev → Test

Create `.github/workflows/ci-test.yml`:

This workflow will:
- Run on PRs to `test` branch
- Run full test suite
- Train model
- Compare with production model
- Generate CML report

### Step 1.4: Create Deployment Workflow

Create `.github/workflows/deploy.yml`:

This workflow will:
- Deploy to staging/production
- Run integration tests
- Update model registry

---

## Step 2: Configure GitHub Secrets

### Step 2.1: Add Required Secrets

Go to: `https://github.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps/settings/secrets/actions`

Add these secrets:

1. **Dagshub Credentials:**
   - `DAGSHUB_USERNAME`: `MasterOz786`
   - `DAGSHUB_TOKEN`: Your Dagshub access token

2. **MLflow Credentials:**
   - `MLFLOW_TRACKING_URI`: `https://dagshub.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps.mlflow`
   - `MLFLOW_USERNAME`: `MasterOz786`
   - `MLFLOW_PASSWORD`: Your Dagshub token (same as DAGSHUB_TOKEN)

3. **DVC Remote (if using):**
   - `DVC_REMOTE_USER`: `MasterOz786`
   - `DVC_REMOTE_PASSWORD`: Your Dagshub token

---

## Step 3: Create Workflow Files

### Workflow 1: CI for Dev Branch (Linting & Testing)

### Workflow 2: CI/CD for Test Branch (Training & Model Comparison)

### Workflow 3: Deployment Workflow

---

## Step 4: Set Up Dagshub CI (Alternative)

Dagshub also supports CI/CD. You can use:
- Dagshub Actions (similar to GitHub Actions)
- Dagshub CI configuration file

---

## Step 5: Test the Workflows

1. Create a feature branch
2. Make changes
3. Create PR to `dev`
4. Watch workflow run
5. Verify all checks pass

---

## Step 6: Model Comparison with CML

Set up Continuous Machine Learning (CML) for model comparison:
- Compare new model vs production
- Generate performance reports
- Auto-approve if metrics improve

---

## Verification Checklist

- [ ] GitHub Actions workflows created
- [ ] Secrets configured in GitHub
- [ ] Workflows trigger on PRs
- [ ] Linting passes
- [ ] Tests pass
- [ ] Model training works in CI
- [ ] Model comparison reports generated
- [ ] Deployment workflow functional

