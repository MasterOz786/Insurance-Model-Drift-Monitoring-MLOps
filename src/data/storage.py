"""
Storage Module for saving processed data to cloud storage (S3/MinIO)
"""

import os
import logging
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_to_storage(**context) -> str:
    """
    Save processed data to cloud storage (S3/MinIO).
    Returns the storage path.
    """
    try:
        # Configuration (should come from environment variables or config)
        storage_type = os.getenv('STORAGE_TYPE', 'local')  # 's3', 'minio', 'local'
        bucket_name = os.getenv('STORAGE_BUCKET', 'mlops')
        
        # Local file path
        local_file = 'data/processed/latest.csv'
        
        if not os.path.exists(local_file):
            raise FileNotFoundError(f"Processed data file not found: {local_file}")
        
        if storage_type == 'local':
            # For local development, just copy to a timestamped location
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dest_path = f'data/processed/archived/{timestamp}_processed.csv'
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            import shutil
            shutil.copy(local_file, dest_path)
            logger.info(f"Data saved locally to: {dest_path}")
            return dest_path
            
        elif storage_type in ['s3', 'minio']:
            # Initialize S3 client (works for both S3 and MinIO)
            endpoint_url = os.getenv('S3_ENDPOINT_URL')
            access_key = os.getenv('AWS_ACCESS_KEY_ID')
            secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            if not endpoint_url:
                raise ValueError("S3_ENDPOINT_URL environment variable is required for MinIO/S3 storage")
            if not access_key or not secret_key:
                raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are required")
            
            logger.info(f"Connecting to {storage_type} at {endpoint_url}")
            s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )
            
            # Check if bucket exists, create if it doesn't
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                logger.info(f"Bucket '{bucket_name}' exists")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    logger.info(f"Bucket '{bucket_name}' not found, creating it...")
                    s3_client.create_bucket(Bucket=bucket_name)
                    logger.info(f"Bucket '{bucket_name}' created successfully")
                else:
                    raise
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f'processed/{timestamp}_processed.csv'
            
            logger.info(f"Uploading {local_file} to {bucket_name}/{s3_key}...")
            s3_client.upload_file(local_file, bucket_name, s3_key)
            logger.info(f"✅ Data uploaded to {storage_type}: s3://{bucket_name}/{s3_key}")
            return f"s3://{bucket_name}/{s3_key}"
        
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
            
    except Exception as e:
        logger.error(f"Failed to save data to storage: {str(e)}")
        raise


if __name__ == "__main__":
    # For local testing
    save_to_storage()

