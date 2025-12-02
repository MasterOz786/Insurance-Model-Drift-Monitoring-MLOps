#!/bin/bash
# Setup Dagshub integration for MLflow and DVC

echo "Setting up Dagshub integration..."

# Get user input
read -p "Enter your Dagshub username: " DAGSHUB_USERNAME
read -p "Enter your Dagshub repository name: " DAGSHUB_REPO
read -p "Enter your Dagshub token: " DAGSHUB_TOKEN

# Set MLflow tracking URI
export MLFLOW_TRACKING_URI="https://dagshub.com/${DAGSHUB_USERNAME}/${DAGSHUB_REPO}.mlflow"

# Configure DVC remote
dvc remote add origin "https://dagshub.com/${DAGSHUB_USERNAME}/${DAGSHUB_REPO}.dvc"
dvc remote modify origin --local auth basic
dvc remote modify origin --local user "${DAGSHUB_USERNAME}"
dvc remote modify origin --local password "${DAGSHUB_TOKEN}"

# Configure MLflow
export MLFLOW_TRACKING_USERNAME="${DAGSHUB_USERNAME}"
export MLFLOW_TRACKING_PASSWORD="${DAGSHUB_TOKEN}"

echo "✅ Dagshub setup complete!"
echo "MLflow Tracking URI: ${MLFLOW_TRACKING_URI}"
echo ""
echo "Add these to your .env file or GitHub Secrets:"
echo "MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI}"
echo "MLFLOW_USERNAME=${DAGSHUB_USERNAME}"
echo "MLFLOW_PASSWORD=${DAGSHUB_TOKEN}"

