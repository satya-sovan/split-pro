"""
Tests for GoCardless service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.gocardless_service import GoCardlessService
from app.models.models import CachedBankData


@pytest.fixture
def mock_db():
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def gocardless_svc():
    """GoCardless service instance"""
    with patch('app.services.gocardless_service.settings') as mock_settings:
        mock_settings.GOCARDLESS_SECRET_ID = 'test-secret-id'
        mock_settings.GOCARDLESS_SECRET_KEY = 'test-secret-key'
        mock_settings.CORS_ORIGINS = ['http://localhost:3000']

        svc = GoCardlessService()
        return svc


class TestGoCardlessService:
    """Test GoCardless service"""

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_access_token(self, mock_client, gocardless_svc):
        """Test getting access token"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access': 'test-access-token',
            'refresh': 'test-refresh-token'
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        token = await gocardless_svc._get_access_token()

        assert token == 'test-access-token'
        assert gocardless_svc.access_token == 'test-access-token'

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_institutions(self, mock_client, gocardless_svc):
        """Test getting institutions list"""
        # Mock token request
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {'access': 'test-token'}

        # Mock institutions request
        inst_response = MagicMock()
        inst_response.status_code = 200
        inst_response.json.return_value = [
            {
                'id': 'BARCLAYS_BARCGB22',
                'name': 'Barclays',
                'bic': 'BARCGB22',
                'logo': 'https://logo.url'
            }
        ]

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = token_response
        mock_client_instance.get.return_value = inst_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        institutions = await gocardless_svc.get_institutions('GB')

        assert len(institutions) == 1
        assert institutions[0]['institution_id'] == 'BARCLAYS_BARCGB22'
        assert institutions[0]['name'] == 'Barclays'
        assert institutions[0]['country'] == 'GB'

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_create_requisition(self, mock_client, gocardless_svc):
        """Test creating a bank requisition"""
        # Mock token
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {'access': 'test-token'}

        # Mock requisition
        req_response = MagicMock()
        req_response.status_code = 201
        req_response.json.return_value = {
            'id': 'req123',
            'link': 'https://ob.gocardless.com/requisitions/req123'
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = req_response
        # First call is token, need to handle both
        mock_client_instance.post.side_effect = [token_response, req_response]
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        result = await gocardless_svc.create_requisition(
            institution_id='BARCLAYS_BARCGB22',
            user_id=1,
            language='en'
        )

        assert result['link'] == 'https://ob.gocardless.com/requisitions/req123'
        assert result['requisition_id'] == 'req123'

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_accounts(self, mock_client, gocardless_svc):
        """Test getting accounts from requisition"""
        # Mock token
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {'access': 'test-token'}

        # Mock accounts
        acc_response = MagicMock()
        acc_response.status_code = 200
        acc_response.json.return_value = {
            'accounts': ['acc1', 'acc2']
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = token_response
        mock_client_instance.get.return_value = acc_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        accounts = await gocardless_svc.get_accounts('req123')

        assert len(accounts) == 2
        assert accounts[0] == 'acc1'

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_get_transactions(self, mock_client, gocardless_svc, mock_db):
        """Test fetching transactions"""
        # Mock token
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {'access': 'test-token'}

        # Mock transactions
        txn_response = MagicMock()
        txn_response.status_code = 200
        txn_response.json.return_value = {
            'transactions': {
                'booked': [
                    {
                        'transactionId': 'txn1',
                        'bookingDate': '2025-12-10',
                        'transactionAmount': {
                            'amount': '50.00',
                            'currency': 'GBP'
                        },
                        'remittanceInformationUnstructured': 'Coffee shop',
                        'creditorName': 'Starbucks'
                    }
                ]
            }
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = token_response
        mock_client_instance.get.return_value = txn_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        mock_db.query.return_value.filter.return_value.first.return_value = None

        transactions = await gocardless_svc.get_transactions(
            account_id='acc1',
            db=mock_db,
            user_id=1
        )

        assert len(transactions) == 1
        assert transactions[0]['transaction_id'] == 'txn1'
        assert transactions[0]['amount'] == 50.00
        assert transactions[0]['currency'] == 'GBP'

    def test_transaction_to_dict(self, gocardless_svc):
        """Test converting GoCardless transaction to dict"""
        gc_txn = {
            'transactionId': 'txn123',
            'bookingDate': '2025-12-10',
            'transactionAmount': {
                'amount': '25.50',
                'currency': 'EUR'
            },
            'remittanceInformationUnstructured': 'Restaurant payment',
            'creditorName': 'Pizza Restaurant'
        }

        result = gocardless_svc._transaction_to_dict(gc_txn)

        assert result['transaction_id'] == 'txn123'
        assert result['amount'] == 25.50
        assert result['currency'] == 'EUR'
        assert result['date'] == '2025-12-10'
        assert result['name'] == 'Restaurant payment'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

