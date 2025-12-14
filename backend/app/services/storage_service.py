"""
Storage service for handling file uploads to S3/R2
Supports both AWS S3 and Cloudflare R2
"""
import boto3
from botocore.client import Config
from typing import Optional

from app.core.config import settings


class StorageService:
    """Service for managing file storage in S3/R2"""

    def __init__(self):
        self.client = None
        self.bucket_name = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize S3 or R2 client based on configuration"""
        # Check for R2 configuration first
        if settings.R2_ACCOUNT_ID and settings.R2_ACCESS_KEY_ID:
            self.client = boto3.client(
                's3',
                endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )
            self.bucket_name = settings.R2_BUCKET_NAME

        # Fall back to AWS S3
        elif settings.AWS_ACCESS_KEY_ID:
            self.client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION or 'us-east-1'
            )
            self.bucket_name = settings.AWS_S3_BUCKET_NAME

    async def get_upload_url(
        self,
        key: str,
        content_type: str,
        file_size: int,
        expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL for uploading a file

        Args:
            key: S3 object key (file path)
            content_type: MIME type of the file
            file_size: Size of file in bytes
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL for uploading
        """
        if not self.client or not self.bucket_name:
            raise ValueError("Storage not configured. Set R2 or AWS S3 credentials.")

        presigned_url = self.client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': key,
                'ContentType': content_type,
            },
            ExpiresIn=expires_in
        )

        return presigned_url

    async def get_download_url(
        self,
        key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL for downloading a file

        Args:
            key: S3 object key (file path)
            expires_in: URL expiration time in seconds

        Returns:
            Presigned URL for downloading
        """
        if not self.client or not self.bucket_name:
            raise ValueError("Storage not configured")

        presigned_url = self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': key,
            },
            ExpiresIn=expires_in
        )

        return presigned_url

    async def delete_file(self, key: str) -> bool:
        """
        Delete a file from storage

        Args:
            key: S3 object key (file path)

        Returns:
            True if successful
        """
        if not self.client or not self.bucket_name:
            return False

        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# Global service instance
storage_service = StorageService()

