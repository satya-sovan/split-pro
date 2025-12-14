"""
Tests for currency rate service
"""
import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.currency_service import CurrencyRateService, currency_service
from app.models.models import CachedCurrencyRate


@pytest.fixture
def mock_db():
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def currency_svc():
    """Currency service instance"""
    return CurrencyRateService()


class TestCurrencyRateService:
    """Test currency rate service"""

    @pytest.mark.asyncio
    async def test_get_rate_same_currency(self, currency_svc, mock_db):
        """Test that same currency returns 1.0"""
        rate = await currency_svc.get_rate(mock_db, "USD", "USD")
        assert rate == 1.0

    @pytest.mark.asyncio
    async def test_get_rate_from_cache(self, currency_svc, mock_db):
        """Test retrieving rate from cache"""
        # Mock cached rate
        cached = MagicMock(spec=CachedCurrencyRate)
        cached.rate = 0.85
        cached.cached_at = datetime.utcnow()

        mock_db.query.return_value.filter.return_value.first.return_value = cached

        rate = await currency_svc.get_rate(mock_db, "USD", "EUR", date(2025, 1, 1))

        assert rate == 0.85
        mock_db.query.assert_called()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_rate_from_api(self, mock_client, currency_svc, mock_db):
        """Test fetching rate from API"""
        # No cached rate
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "rates": {"EUR": 0.85},
            "base": "USD",
            "date": "2025-01-01"
        }
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        rate = await currency_svc.get_rate(mock_db, "USD", "EUR", date(2025, 1, 1))

        assert rate == 0.85
        mock_client_instance.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_batch_rates(self, currency_svc, mock_db):
        """Test batch rate fetching"""
        with patch.object(currency_svc, 'get_rate', new=AsyncMock(side_effect=[0.85, 1.2, 110.5])):
            rates = await currency_svc.get_batch_rates(
                mock_db,
                ["EUR", "GBP", "JPY"],
                "USD",
                date(2025, 1, 1)
            )

            assert len(rates) == 3
            assert rates["EUR"] == 0.85
            assert rates["GBP"] == 1.2
            assert rates["JPY"] == 110.5

    def test_cache_rate(self, currency_svc, mock_db):
        """Test caching a rate"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        currency_svc._cache_rate(
            mock_db,
            "USD",
            "EUR",
            date(2025, 1, 1),
            0.85
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_cache_rate_update_existing(self, currency_svc, mock_db):
        """Test updating existing cached rate"""
        existing = MagicMock(spec=CachedCurrencyRate)
        existing.rate = 0.83
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        currency_svc._cache_rate(
            mock_db,
            "USD",
            "EUR",
            date(2025, 1, 1),
            0.85
        )

        assert existing.rate == 0.85
        mock_db.add.assert_not_called()  # Should update, not add
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_rate_api_error_fallback(self, mock_client, currency_svc, mock_db):
        """Test API error falls back to 1.0"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = Exception("API Error")
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        rate = await currency_svc.get_rate(mock_db, "USD", "EUR", date(2025, 1, 1))

        assert rate == 1.0  # Fallback


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

