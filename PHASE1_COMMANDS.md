# Phase 1: Data Ingestion - Command Checklist

Run these commands in order to complete Phase 1 and gather all required screenshots.

---

## Step 1: Data Extraction (2.1)

### 1.1 Test API Connection
```bash
# Test Alpha Vantage API with curl
curl "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=60min&apikey=0152NEAOLLREWETG" | python3 -m json.tool | head -30
```

**Screenshot**: API response showing JSON data

### 1.2 Extract Data Using Python Script
```bash
# Make sure .env file exists with API key
cat .env

# Run data extraction
python src/data/ingestion.py
```

**Expected Output**: 
- ✅ Success message
- ✅ Data saved to `data/raw/latest_extract.csv`
- ✅ Number of data points extracted

**Screenshots to Take**:
1. Terminal showing successful extraction
2. Data file in `data/raw/` directory
3. First few rows of extracted data

---

## Step 2: Data Quality Check (Mandatory Quality Gate)

### 2.1 Run Quality Check
```bash
# Run quality validation
python src/data/quality_check.py
```

**Expected Output**:
- ✅ All quality checks passed
- ✅ Null value checks
- ✅ Schema validation
- ✅ Data volume check

**Screenshots to Take**:
1. Quality check passing (all ✅ marks)
2. Quality check code implementation

### 2.2 Test Quality Check Failure (Optional but Recommended)
```bash
# Create a bad data file to test failure
python3 -c "
import pandas as pd
import numpy as np
df = pd.DataFrame({
    'AnnualPremium': [1000, np.nan, np.nan, np.nan, 2000],  # >1% null
    'Age': [25, 30, 35, 40, 45],
    'RegionID': [1, 2, 3, 4, 5],
    'Gender': ['M', 'F', 'M', 'F', 'M']
})
df.to_csv('data/raw/latest_extract.csv', index=False)
"

# Run quality check (should fail)
python src/data/quality_check.py
```

**Screenshot**: Quality check failing (shows error)

---

## Step 3: Data Transformation

### 3.1 Run Transformation
```bash
# Transform the data
python src/data/transformation.py
```

**Expected Output**:
- ✅ Features created (lag features, rolling stats)
- ✅ Data saved to `data/processed/latest.csv`

**Screenshots to Take**:
1. Transformation code
2. Before transformation (raw data)
3. After transformation (processed data with new features)
4. Feature statistics

### 3.2 View Transformed Data
```bash
# View processed data
head -20 data/processed/latest.csv

# Check data shape and features
python3 -c "
import pandas as pd
df = pd.read_csv('data/processed/latest.csv', index_col=0, parse_dates=True)
print(f'Shape: {df.shape}')
print(f'Columns: {list(df.columns)}')
print(f'\nFirst 5 rows:')
print(df.head())
print(f'\nStatistics:')
print(df.describe())
"
```

**Screenshot**: Transformed data with new features

---

## Step 4: Data Profiling Report

### 4.1 Generate Profiling Report
```bash
# Generate data profiling report
python src/data/profiling.py data/processed/latest.csv data/reports/profile.html
```

**Expected Output**:
- ✅ Report generated successfully
- ✅ HTML file created at `data/reports/profile.html`

**Screenshots to Take**:
1. Command execution
2. Generated HTML report (open in browser)
3. Report showing statistics, distributions, correlations

### 4.2 View Profiling Report
```bash
# Open the report (macOS)
open data/reports/profile.html

# Or view file location
ls -lh data/reports/
```

**Screenshot**: Profiling report in browser showing all sections

---

## Step 5: Data Storage (S3/MinIO)

### 5.1 For Local Development (MinIO - Optional)
```bash
# Start MinIO using Docker
docker run -d -p 9000:9000 -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"

# Wait a few seconds, then access MinIO console
open http://localhost:9001
```

**Screenshots to Take**:
1. MinIO console login page
2. MinIO console showing buckets
3. Uploaded data file in MinIO

### 5.2 Save to Storage
```bash
# Update .env with storage config (if using MinIO)
echo "STORAGE_TYPE=minio" >> .env
echo "S3_ENDPOINT_URL=http://localhost:9000" >> .env
echo "AWS_ACCESS_KEY_ID=minioadmin" >> .env
echo "AWS_SECRET_ACCESS_KEY=minioadmin" >> .env
echo "STORAGE_BUCKET=mlops-data" >> .env

# Run storage script
python src/data/storage.py
```

**Screenshots to Take**:
1. Storage code execution
2. Data uploaded to storage (MinIO console or S3)
3. File listing in storage bucket

**Note**: For local development, you can skip MinIO and just use local storage. The storage.py script will save locally if STORAGE_TYPE=local.

---

## Step 6: DVC Versioning

### 6.1 Initialize DVC (if not done)
```bash
# Check if DVC is initialized
ls -la .dvc/

# If not, initialize
dvc init
git add .dvc .gitignore
git commit -m "Initialize DVC"
```

### 6.2 Configure DVC Remote (Dagshub or S3)
```bash
# For Dagshub (recommended)
dvc remote add origin https://dagshub.com/your-username/your-repo.dvc
dvc remote modify origin --local auth basic
dvc remote modify origin --local user your-username
dvc remote modify origin --local password your-token

# Verify remote
dvc remote list
```

**Screenshot**: DVC remote configuration

### 6.3 Add and Version Data
```bash
# Add processed data to DVC
dvc add data/processed/latest.csv

# Check what was created
ls -la data/processed/
cat data/processed/latest.csv.dvc

# Commit DVC metadata to Git
git add data/processed/latest.csv.dvc data/processed/.gitignore
git commit -m "Add processed data with DVC"

# Push data to remote storage
dvc push
```

**Screenshots to Take**:
1. `dvc add` command output
2. `.dvc` file in Git (showing metadata)
3. Data in DVC remote (Dagshub UI or S3)
4. Git commit showing .dvc file

---

## Complete Phase 1 Verification

### Run All Steps in Sequence
```bash
# 1. Extract
python src/data/ingestion.py

# 2. Quality Check
python src/data/quality_check.py

# 3. Transform
python src/data/transformation.py

# 4. Profile
python src/data/profiling.py data/processed/latest.csv data/reports/profile.html

# 5. Storage (local)
python src/data/storage.py

# 6. DVC Version
dvc add data/processed/latest.csv
git add data/processed/latest.csv.dvc data/processed/.gitignore
git commit -m "Phase 1: Data pipeline complete"
dvc push
```

### Verify All Files Created
```bash
# Check all required files exist
echo "=== Raw Data ==="
ls -lh data/raw/

echo "=== Processed Data ==="
ls -lh data/processed/

echo "=== Reports ==="
ls -lh data/reports/

echo "=== DVC Files ==="
ls -la data/processed/*.dvc 2>/dev/null || echo "No DVC files yet"
```

---

## Screenshot Checklist for Phase 1

- [ ] **API Selection**: Alpha Vantage website/API key page
- [ ] **API Test**: curl command showing JSON response
- [ ] **Data Extraction**: Python script execution and output
- [ ] **Raw Data**: File in `data/raw/` directory
- [ ] **Quality Check Pass**: All checks passing
- [ ] **Quality Check Fail**: (Optional) Quality check failing
- [ ] **Transformation**: Code and before/after data
- [ ] **Profiling Report**: HTML report in browser
- [ ] **Storage**: Data in MinIO/S3 (or local confirmation)
- [ ] **DVC Add**: Command output
- [ ] **DVC Files**: `.dvc` file in Git
- [ ] **DVC Remote**: Data in Dagshub/S3

---

## Quick Reference: All Commands

```bash
# Complete Phase 1 Pipeline
python src/data/ingestion.py                    # Extract
python src/data/quality_check.py                # Quality gate
python src/data/transformation.py               # Transform
python src/data/profiling.py data/processed/latest.csv data/reports/profile.html  # Profile
python src/data/storage.py                      # Store
dvc add data/processed/latest.csv               # Version
git add data/processed/latest.csv.dvc data/processed/.gitignore
git commit -m "Phase 1 complete"
dvc push                                        # Push to remote
```

---

## Troubleshooting

### If ingestion fails:
```bash
# Check API key
cat .env | grep ALPHA_VANTAGE_API_KEY

# Test API directly
curl "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=60min&apikey=0152NEAOLLREWETG" | head -20
```

### If quality check fails:
```bash
# Check data file exists
ls -lh data/raw/latest_extract.csv

# View data
head -5 data/raw/latest_extract.csv
```

### If transformation fails:
```bash
# Check if raw data exists
ls -lh data/raw/

# Check Python path
python --version
```

---

**Run these commands in order and take screenshots at each step!**

