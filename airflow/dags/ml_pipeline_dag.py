"""
MLOps Pipeline DAG for Real-Time Predictive System
Orchestrates: Data Extraction → Quality Check → Transformation → Training → Model Registration
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from data.ingestion import extract_data
from data.quality_check import validate_data_quality
from data.transformation import transform_data
from data.profiling import generate_data_profile
from data.storage import save_to_storage
from training.train import train_model
from training.register import register_model

# Default arguments
default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'ml_pipeline_dag',
    default_args=default_args,
    description='End-to-end MLOps pipeline: ETL → Training → Registration',
    schedule_interval='@daily',  # Run daily
    start_date=datetime(2025, 12, 2),
    catchup=False,
    tags=['mlops', 'training', 'etl'],
)

# Task 1: Extract data from API
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

# Task 2: Data Quality Check (Mandatory Quality Gate)
quality_check_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag,
)

# Task 3: Transform and feature engineering
transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

# Task 4: Generate data profiling report
profile_task = PythonOperator(
    task_id='generate_data_profile',
    python_callable=lambda: generate_data_profile('data/processed/latest.csv', 'data/reports/profile.html'),
    dag=dag,
)

# Task 5: Save to storage (S3/MinIO) and version with DVC
save_storage_task = PythonOperator(
    task_id='save_to_storage',
    python_callable=save_to_storage,
    dag=dag,
)

dvc_version_task = BashOperator(
    task_id='dvc_version_data',
    bash_command='cd /Users/masteroz/Desktop/22i-2434/Side-Kicks/Insurance-Model-Drift-Monitoring-MLOps && dvc add data/processed/latest.csv && dvc push',
    dag=dag,
)

# Task 6: Train model
train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

# Task 7: Register model in MLflow
register_task = PythonOperator(
    task_id='register_model',
    python_callable=register_model,
    dag=dag,
)

# Define task dependencies
extract_task >> quality_check_task >> transform_task >> profile_task
transform_task >> save_storage_task >> dvc_version_task
transform_task >> train_task >> register_task

