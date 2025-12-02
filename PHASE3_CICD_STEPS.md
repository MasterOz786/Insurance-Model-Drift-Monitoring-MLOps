# Phase III — CI/CD Step-by-Step Guide

## Overview
Set up Continuous Integration and Continuous Deployment (CI/CD) using GitHub Actions and Dagshub to automate testing, model training, and deployment.

---

## Step 1: Configure GitHub Secrets

### Step 1.1: Access GitHub Secrets

1. Go to your repository: `https://github.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Step 1.2: Add Required Secrets

Add these secrets one by one:

#### MLflow & Dagshub Secrets:
```
Name: MLFLOW_TRACKING_URI
Value: https://dagshub.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps.mlflow
```

```
Name: MLFLOW_USERNAME
Value: MasterOz786
```

```
Name: MLFLOW_PASSWORD
Value: <your_dagshub_token>
```

#### DVC Secrets (if using DVC remote):
```
Name: DVC_REMOTE_USER
Value: MasterOz786
```

```
Name: DVC_REMOTE_PASSWORD
Value: <your_dagshub_token>
```

#### Docker Secrets (for deployment):
```
Name: DOCKER_USERNAME
Value: <your_dockerhub_username>
```

```
Name: DOCKER_PASSWORD
Value: <your_dockerhub_token>
```

**Note:** Get your Dagshub token from: https://dagshub.com/MasterOz786/Insurance-Model-Drift-Monitoring-MLOps/settings/tokens

---

## Step 2: Create Required Scripts

### Step 2.1: Create Model Comparison Script

Create `scripts/compare_models.py`:

This script will compare staging vs production models and generate a CML report.

### Step 2.2: Create Get Best Model Script

Create `scripts/get_best_model.py`:

This script will fetch the best model version from MLflow for deployment.

---

## Step 3: Update Workflow Files

### Step 3.1: Review CI-Dev Workflow

The workflow `.github/workflows/ci-dev.yml` already exists and will:
- Run on PRs to `dev` branch
- Lint code with Black
- Run unit tests
- Upload coverage

**Verify it works:**
- Create a feature branch
- Make a small change
- Create PR to `dev`
- Check Actions tab

### Step 3.2: Review CI-Test Workflow

The workflow `.github/workflows/ci-test.yml` will:
- Run on PRs to `test` branch
- Pull data from DVC
- Train model
- Compare models with CML
- Post report to PR

**Needs:**
- `scripts/compare_models.py` script
- CML setup

### Step 3.3: Review CD-Master Workflow

The workflow `.github/workflows/cd-master.yml` will:
- Run on merge to `master`
- Build Docker image
- Push to Docker Hub
- Deploy to staging

**Needs:**
- `scripts/get_best_model.py` script
- Docker Hub credentials

---

## Step 4: Test Workflow 1 (CI-Dev)

### Step 4.1: Create Test Branch

```bash
git checkout -b feature/test-ci
```

### Step 4.2: Make a Small Change

```bash
# Make a small code change or add a comment
echo "# Test CI" >> src/training/train.py
```

### Step 4.3: Commit and Push

```bash
git add .
git commit -m "Test CI workflow"
git push -u origin feature/test-ci
```

### Step 4.4: Create PR to Dev

1. Go to GitHub
2. Create Pull Request: `feature/test-ci` → `dev`
3. Watch the Actions tab
4. Verify workflow runs and passes

**Expected Results:**
- ✅ Code formatting check passes
- ✅ Linting passes
- ✅ Unit tests pass
- ✅ Coverage uploaded

---

## Step 5: Test Workflow 2 (CI-Test with Model Training)

### Step 5.1: Create Comparison Script

First, create the model comparison script.

### Step 5.2: Create Test Branch

```bash
git checkout dev
git checkout -b feature/test-model-training
```

### Step 5.3: Create PR to Test Branch

1. Create PR: `feature/test-model-training` → `test`
2. Watch workflow run
3. Verify:
   - DVC data pulled
   - Model training executes
   - CML report generated
   - Report posted to PR

---

## Step 6: Test Workflow 3 (CD-Master)

### Step 6.1: Create Get Best Model Script

Create the script to fetch model version.

### Step 6.2: Merge to Master

```bash
git checkout test
git merge dev
git push origin test
# Then merge test → master via PR
```

### Step 6.3: Verify Deployment

- Check Docker image built
- Verify image pushed to Docker Hub
- Check deployment logs

---

## Step 7: Set Up Branch Protection

### Step 7.1: Protect Dev Branch

1. Go to: Settings → Branches
2. Add rule for `dev`:
   - Require pull request reviews (1 approval)
   - Require status checks to pass
   - Require branches to be up to date

### Step 7.2: Protect Test Branch

Same as dev, but require:
- CI-Dev workflow to pass
- Model comparison to pass

### Step 7.3: Protect Master Branch

Require:
- All previous checks
- CD workflow to pass
- Manual approval (optional)

---

## Step 8: Dagshub CI (Alternative)

### Step 8.1: Enable Dagshub CI

1. Go to Dagshub repository
2. Settings → CI/CD
3. Enable Dagshub Actions

### Step 8.2: Create Dagshub Workflow

Similar to GitHub Actions but runs on Dagshub infrastructure.

---

## Verification Checklist

### GitHub Actions:
- [ ] Secrets configured
- [ ] CI-Dev workflow runs on PR
- [ ] CI-Test workflow runs on PR
- [ ] CD-Master workflow runs on merge
- [ ] All workflows pass

### Scripts:
- [ ] `scripts/compare_models.py` created
- [ ] `scripts/get_best_model.py` created
- [ ] Scripts work in CI environment

### Branch Protection:
- [ ] Dev branch protected
- [ ] Test branch protected
- [ ] Master branch protected

### Model Training in CI:
- [ ] DVC data pulls successfully
- [ ] Model training completes
- [ ] MLflow logging works
- [ ] Model comparison works

### Deployment:
- [ ] Docker image builds
- [ ] Image pushed to registry
- [ ] Deployment successful
- [ ] Health checks pass

---

## Quick Reference Commands

```bash
# Test CI locally (simulate GitHub Actions)
act -j code-quality

# Check workflow syntax
yamllint .github/workflows/*.yml

# Test scripts locally
python scripts/compare_models.py
python scripts/get_best_model.py
```

---

## Troubleshooting

### Issue: Workflow fails on secret access
**Solution:** Verify secrets are set correctly in GitHub Settings

### Issue: DVC pull fails
**Solution:** Check DVC remote configuration and credentials

### Issue: Model training fails in CI
**Solution:** Check MLflow credentials and tracking URI

### Issue: Docker build fails
**Solution:** Verify Docker Hub credentials and Dockerfile

---

## Next Steps

After Phase III is complete:
1. ✅ Automated testing on every PR
2. ✅ Automated model training and comparison
3. ✅ Automated deployment
4. → **Phase IV**: Monitoring & Alerting (if applicable)
