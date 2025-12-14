"""
Tests for Plaid service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.plaid_service import PlaidService
from app.models.models import User


@pytest.fixture
def mock_db():
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def plaid_svc():
    """Plaid service instance"""
    with patch('app.services.plaid_service.settings') as mock_settings:
        mock_settings.PLAID_CLIENT_ID = 'test-client-id'
        mock_settings.PLAID_SECRET = 'test-secret'
        mock_settings.PLAID_ENV = 'sandbox'
        mock_settings.CORS_ORIGINS = ['http://localhost:3000']

        svc = PlaidService()
        return svc


class TestPlaidService:
    """Test Plaid service"""

    @pytest.mark.asyncio
    @patch('plaid.api.plaid_api.PlaidApi.link_token_create')
    async def test_create_link_token(self, mock_create, plaid_svc):
        """Test creating Plaid Link token"""
        mock_create.return_value = {
            'link_token': 'link-sandbox-test-token',
            'expiration': '2025-12-11T12:00:00Z'
        }

        result = await plaid_svc.create_link_token(
            user_id=1,
            user_name="Test User",
            language='en'
        )

        assert 'link_token' in result
        assert 'expiration' in result
        assert result['link_token'] == 'link-sandbox-test-token'

    @pytest.mark.asyncio
    @patch('plaid.api.plaid_api.PlaidApi.item_public_token_exchange')
    async def test_exchange_public_token(self, mock_exchange, plaid_svc, mock_db):
        """Test exchanging public token for access token"""
        mock_exchange.return_value = {
            'access_token': 'access-sandbox-test-token',
            'item_id': 'test-item-id'
        }

        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = await plaid_svc.exchange_public_token(
            public_token='public-sandbox-test-token',
            db=mock_db,
            user_id=1
        )

        assert result['access_token'] == 'access-sandbox-test-token'
        assert result['item_id'] == 'test-item-id'
        assert mock_user.obapi_provider_id == 'access-sandbox-test-token'
        assert mock_user.banking_id == 'test-item-id'

    @pytest.mark.asyncio
    @patch('plaid.api.plaid_api.PlaidApi.transactions_get')
    async def test_get_transactions(self, mock_get, plaid_svc, mock_db):
        """Test fetching transactions from Plaid"""
        mock_get.return_value = {
            'transactions': [
                {
                    'transaction_id': 'txn1',
                    'account_id': 'acc1',
                    'amount': 50.00,
                    'date': '2025-12-10',
                    'name': 'Coffee Shop',
                    'merchant_name': 'Starbucks',
                    'category': ['Food and Drink', 'Restaurants'],
                    'pending': False,
                    'iso_currency_code': 'USD',
                    'payment_channel': 'in_store'
                }
            ],
            'total_transactions': 1
        }

        mock_db.query.return_value.filter.return_value.first.return_value = None

        start_date = datetime(2025, 12, 1)
        end_date = datetime(2025, 12, 10)

        transactions = await plaid_svc.get_transactions(
            access_token='test-access-token',
            start_date=start_date,
            end_date=end_date,
            db=mock_db,
            user_id=1
        )

        assert len(transactions) == 1
        assert transactions[0]['transaction_id'] == 'txn1'
        assert transactions[0]['amount'] == 50.00
        assert transactions[0]['name'] == 'Coffee Shop'

    @pytest.mark.asyncio
    async def test_get_institutions(self, plaid_svc):
        """Test getting institution list"""
        institutions = await plaid_svc.get_institutions('US')

        assert isinstance(institutions, list)
        assert len(institutions) > 0
        assert 'institution_id' in institutions[0]
        assert 'name' in institutions[0]

    def test_transaction_to_dict(self, plaid_svc):
        """Test converting Plaid transaction to dict"""
        plaid_txn = {
            'transaction_id': 'txn123',
            'account_id': 'acc123',
            'amount': 25.50,
            'date': '2025-12-10',
            'name': 'Restaurant',
            'merchant_name': 'Pizza Place',
            'category': ['Food and Drink'],
            'pending': False,
            'iso_currency_code': 'USD',
            'payment_channel': 'online'
        }

        result = plaid_svc._transaction_to_dict(plaid_txn)

        assert result['transaction_id'] == 'txn123'
        assert result['amount'] == 25.50
        assert result['currency'] == 'USD'
        assert result['name'] == 'Restaurant'
        assert result['pending'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

