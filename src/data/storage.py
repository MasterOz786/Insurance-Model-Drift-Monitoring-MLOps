"""
Storage Module for saving processed data to cloud storage (S3/MinIO)
"""

import os
import logging
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

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
        bucket_name = os.getenv('STORAGE_BUCKET', 'mlops-data')
        
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
            s3_client = boto3.client(
                's3',
                endpoint_url=os.getenv('S3_ENDPOINT_URL'),  # For MinIO
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            )
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f'processed/{timestamp}_processed.csv'
            
            s3_client.upload_file(local_file, bucket_name, s3_key)
            logger.info(f"Data uploaded to {storage_type}: s3://{bucket_name}/{s3_key}")
            return f"s3://{bucket_name}/{s3_key}"
        
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
            
    except Exception as e:
        logger.error(f"Failed to save data to storage: {str(e)}")
        raise


if __name__ == "__main__":
    # For local testing
    save_to_storage()

