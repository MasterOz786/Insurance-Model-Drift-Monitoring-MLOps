# Repository Structure for MLOps Real-Time Predictive System

```
Insurance-Model-Drift-Monitoring-MLOps/
│
├── .github/
│   └── workflows/
│       ├── ci-dev.yml          # CI for feature → dev (linting, unit tests)
│       ├── ci-test.yml         # CI for dev → test (model retraining + CML)
│       └── cd-master.yml       # CD for test → master (Docker build & deploy)
│
├── airflow/
│   ├── dags/
│   │   ├── __init__.py
│   │   └── ml_pipeline_dag.py  # Main Airflow DAG for ETL → Training
│   ├── plugins/
│   │   └── __init__.py
│   └── requirements.txt        # Airflow-specific dependencies
│
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── ingestion.py       # API data extraction
│   │   ├── quality_check.py   # Data quality validation
│   │   ├── transformation.py   # Feature engineering
│   │   └── storage.py          # Save to S3/MinIO
│   │
│   ├── training/
│   │   ├── __init__.py
│   │   ├── train.py            # Model training script
│   │   ├── evaluate.py         # Model evaluation
│   │   └── register.py         # MLflow model registration
│   │
│   ├── serving/
│   │   ├── __init__.py
│   │   ├── api.py              # FastAPI application
│   │   ├── model_loader.py     # Load model from MLflow
│   │   └── prometheus.py       # Prometheus metrics exporter
│   │
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── drift_detection.py  # Data drift detection
│   │   └── metrics.py          # Custom Prometheus metrics
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration management
│       ├── logging.py          # Logging setup
│       └── mlflow_client.py    # MLflow client wrapper
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_data_quality.py
│   │   ├── test_transformation.py
│   │   └── test_training.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_pipeline.py
│   └── fixtures/
│       └── sample_data.json
│
├── docker/
│   ├── Dockerfile.api          # FastAPI service container
│   ├── Dockerfile.airflow      # Airflow container
│   ├── docker-compose.yml      # Local development setup
│   └── prometheus/
│       └── prometheus.yml       # Prometheus configuration
│
├── monitoring/
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   └── mlops-dashboard.json
│   │   └── provisioning/
│   │       └── datasources.yml
│   └── alerts/
│       └── alert_rules.yml     # Grafana alert rules
│
├── config/
│   ├── config.yml              # Main configuration
│   ├── api_config.yml          # API configuration
│   ├── mlflow_config.yml       # MLflow settings
│   └── monitoring_config.yml   # Monitoring settings
│
├── data/
│   ├── raw/                    # Raw data from APIs (gitignored)
│   ├── processed/              # Processed datasets (DVC versioned)
│   └── reports/                # Pandas profiling reports
│
├── models/                     # Local model cache (gitignored)
│
├── notebooks/
│   ├── exploration.ipynb
│   ├── monitoring.ipynb
│   └── drift_analysis.ipynb
│
├── scripts/
│   ├── setup_dagshub.sh        # Setup Dagshub integration
│   ├── setup_minio.sh          # Setup MinIO for data storage
│   └── deploy.sh               # Deployment script
│
├── .dvc/                       # DVC metadata
├── .github/
├── .gitignore
├── .dockerignore
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.py                   # Package setup
├── Makefile
├── README.md
└── LICENSE
```

## Key Components Explained

### 1. **Airflow DAGs** (`airflow/dags/`)
- Main DAG orchestrates: Extraction → Quality Check → Transformation → Training → Model Registration

### 2. **Source Code** (`src/`)
- **data/**: ETL pipeline components
- **training/**: Model training and evaluation
- **serving/**: FastAPI service with Prometheus metrics
- **monitoring/**: Drift detection and custom metrics
- **utils/**: Shared utilities

### 3. **CI/CD** (`.github/workflows/`)
- **ci-dev.yml**: Code quality checks for feature → dev
- **ci-test.yml**: Model retraining + CML comparison for dev → test
- **cd-master.yml**: Docker build & push for test → master

### 4. **Docker** (`docker/`)
- Separate containers for API service and Airflow
- Docker Compose for local development

### 5. **Monitoring** (`monitoring/`)
- Grafana dashboards and alert configurations
- Prometheus configuration

### 6. **Configuration** (`config/`)
- Centralized configuration files for different components

