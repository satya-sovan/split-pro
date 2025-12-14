"""
Tests for storage service (S3/R2)
"""
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

from app.services.storage_service import StorageService


@pytest.fixture
def mock_s3_client():
    """Mock boto3 S3 client"""
    return MagicMock()


@pytest.fixture
def storage_svc(mock_s3_client):
    """Storage service instance with mocked client"""
    svc = StorageService()
    svc.client = mock_s3_client
    svc.bucket_name = "test-bucket"
    return svc


class TestStorageService:
    """Test storage service"""

    @pytest.mark.asyncio
    async def test_get_upload_url_success(self, storage_svc, mock_s3_client):
        """Test generating presigned upload URL"""
        mock_s3_client.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/upload?signed"

        url = await storage_svc.get_upload_url(
            key="user/123/file.jpg",
            content_type="image/jpeg",
            file_size=1024000
        )

        assert url == "https://test-bucket.s3.amazonaws.com/upload?signed"
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'put_object',
            Params={
                'Bucket': 'test-bucket',
                'Key': 'user/123/file.jpg',
                'ContentType': 'image/jpeg',
            },
            ExpiresIn=3600
        )

    @pytest.mark.asyncio
    async def test_get_upload_url_not_configured(self):
        """Test error when storage not configured"""
        svc = StorageService()
        svc.client = None

        with pytest.raises(ValueError, match="Storage not configured"):
            await svc.get_upload_url(
                key="test.jpg",
                content_type="image/jpeg",
                file_size=1024
            )

    @pytest.mark.asyncio
    async def test_get_download_url_success(self, storage_svc, mock_s3_client):
        """Test generating presigned download URL"""
        mock_s3_client.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/download?signed"

        url = await storage_svc.get_download_url(key="user/123/file.jpg")

        assert url == "https://test-bucket.s3.amazonaws.com/download?signed"
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': 'test-bucket',
                'Key': 'user/123/file.jpg',
            },
            ExpiresIn=3600
        )

    @pytest.mark.asyncio
    async def test_get_download_url_custom_expiry(self, storage_svc, mock_s3_client):
        """Test download URL with custom expiration"""
        mock_s3_client.generate_presigned_url.return_value = "https://test.com/file"

        await storage_svc.get_download_url(key="test.jpg", expires_in=7200)

        call_args = mock_s3_client.generate_presigned_url.call_args
        assert call_args.kwargs['ExpiresIn'] == 7200

    @pytest.mark.asyncio
    async def test_delete_file_success(self, storage_svc, mock_s3_client):
        """Test deleting file from storage"""
        mock_s3_client.delete_object.return_value = {}

        result = await storage_svc.delete_file(key="user/123/file.jpg")

        assert result is True
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='user/123/file.jpg'
        )

    @pytest.mark.asyncio
    async def test_delete_file_error(self, storage_svc, mock_s3_client):
        """Test error handling when deleting file"""
        mock_s3_client.delete_object.side_effect = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'delete_object'
        )

        result = await storage_svc.delete_file(key="nonexistent.jpg")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_file_not_configured(self):
        """Test delete when storage not configured"""
        svc = StorageService()
        svc.client = None

        result = await svc.delete_file(key="test.jpg")
        assert result is False

    @patch('boto3.client')
    def test_initialize_r2_client(self, mock_boto_client):
        """Test initializing R2 client"""
        from app.core.config import settings

        # Temporarily set R2 credentials
        original_r2_account = settings.R2_ACCOUNT_ID
        original_r2_key = settings.R2_ACCESS_KEY_ID

        settings.R2_ACCOUNT_ID = "test-account"
        settings.R2_ACCESS_KEY_ID = "test-key"
        settings.R2_SECRET_ACCESS_KEY = "test-secret"
        settings.R2_BUCKET_NAME = "test-r2-bucket"

        svc = StorageService()

        # Restore original values
        settings.R2_ACCOUNT_ID = original_r2_account
        settings.R2_ACCESS_KEY_ID = original_r2_key

        # Should have initialized with R2 endpoint
        mock_boto_client.assert_called()
        call_kwargs = mock_boto_client.call_args.kwargs
        assert 'endpoint_url' in call_kwargs
        assert 'r2.cloudflarestorage.com' in call_kwargs['endpoint_url']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

