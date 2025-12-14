"""
Integration tests for new expense endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import date

from app.main import app
from app.api.deps import get_current_user
from app.models.models import User


# Mock user for testing
def mock_current_user():
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        currency="USD",
        preferred_language="en"
    )
    return user


app.dependency_overrides[get_current_user] = mock_current_user
client = TestClient(app)


class TestCurrencyRateEndpoints:
    """Test currency rate API endpoints"""

    @patch('app.api.routers.expense.currency_service')
    def test_get_currency_rate(self, mock_currency_service):
        """Test GET /expenses/currency-rate"""
        mock_currency_service.get_rate = AsyncMock(return_value=0.85)

        response = client.get(
            "/api/expenses/currency-rate",
            params={
                "from_currency": "USD",
                "to_currency": "EUR",
                "date": "2025-01-01"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "rate" in data

    def test_get_currency_rate_invalid_date(self):
        """Test currency rate with invalid date format"""
        response = client.get(
            "/api/expenses/currency-rate",
            params={
                "from_currency": "USD",
                "to_currency": "EUR",
                "date": "invalid-date"
            }
        )

        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

    @patch('app.api.routers.expense.currency_service')
    def test_get_batch_currency_rates(self, mock_currency_service):
        """Test POST /expenses/currency-rates/batch"""
        mock_currency_service.get_batch_rates = AsyncMock(return_value={
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.5
        })

        response = client.post(
            "/api/expenses/currency-rates/batch",
            params={
                "from_currencies": ["EUR", "GBP", "JPY"],
                "to_currency": "USD"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "rates" in data


class TestUploadUrlEndpoint:
    """Test file upload URL endpoint"""

    @patch('app.api.routers.expense.storage_service')
    def test_get_upload_url(self, mock_storage_service):
        """Test POST /expenses/upload-url"""
        mock_storage_service.get_upload_url = AsyncMock(
            return_value="https://bucket.s3.amazonaws.com/presigned-url"
        )

        response = client.post(
            "/api/expenses/upload-url",
            params={
                "file_name": "receipt.jpg",
                "file_type": "image/jpeg",
                "file_size": 1024000
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "upload_url" in data
        assert "key" in data

    def test_get_upload_url_file_too_large(self):
        """Test upload URL with file size exceeding limit"""
        response = client.post(
            "/api/expenses/upload-url",
            params={
                "file_name": "large.jpg",
                "file_type": "image/jpeg",
                "file_size": 20 * 1024 * 1024  # 20MB
            }
        )

        assert response.status_code == 400
        assert "exceeds 10MB limit" in response.json()["detail"]


class TestRecurringExpensesEndpoint:
    """Test recurring expenses endpoint"""

    def test_get_recurring_expenses(self):
        """Test GET /expenses/recurring"""
        response = client.get("/api/expenses/recurring")

        # Should return empty list initially
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestFriendExpensesEndpoint:
    """Test friend expenses endpoint"""

    def test_get_expenses_with_friend(self):
        """Test GET /expenses/friend/{friend_id}"""
        response = client.get("/api/expenses/friend/2")

        # Should return empty list initially (no expenses)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_expenses_with_friend_include_deleted(self):
        """Test friend expenses including deleted"""
        response = client.get(
            "/api/expenses/friend/2",
            params={"include_deleted": True}
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

