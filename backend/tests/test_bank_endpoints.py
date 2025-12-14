"""
Integration tests for bank transaction endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.api.deps import get_current_user
from app.models.models import User


def mock_current_user():
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        currency="USD",
        preferred_language="en",
        obapi_provider_id=None,
        banking_id=None
    )
    return user


app.dependency_overrides[get_current_user] = mock_current_user
client = TestClient(app)


class TestBankEndpoints:
    """Test bank transaction endpoints"""

    @patch('app.api.routers.bank.plaid_service')
    def test_get_institutions_plaid(self, mock_plaid):
        """Test GET /bank/institutions with Plaid"""
        mock_plaid.get_institutions.return_value = AsyncMock(return_value=[
            {
                'institution_id': 'ins_1',
                'name': 'Chase',
                'country': 'US',
                'logo': None
            }
        ])

        with patch('app.api.routers.bank.get_active_provider', return_value='plaid'):
            response = client.get("/api/bank/institutions", params={"country_code": "US"})

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_get_institutions_not_configured(self):
        """Test institutions when no provider configured"""
        with patch('app.api.routers.bank.get_active_provider', return_value=None):
            response = client.get("/api/bank/institutions")

            assert response.status_code == 501
            assert "not configured" in response.json()["detail"].lower()

    @patch('app.api.routers.bank.plaid_service')
    def test_connect_to_bank_plaid(self, mock_plaid):
        """Test POST /bank/connect with Plaid"""
        mock_plaid.create_link_token.return_value = AsyncMock(return_value={
            'link_token': 'link-sandbox-token',
            'expiration': '2025-12-11T12:00:00Z'
        })

        with patch('app.api.routers.bank.get_active_provider', return_value='plaid'):
            response = client.post("/api/bank/connect")

            assert response.status_code == 200
            data = response.json()
            assert 'link_token' in data

    @patch('app.api.routers.bank.gocardless_service')
    def test_connect_to_bank_gocardless(self, mock_gc):
        """Test POST /bank/connect with GoCardless"""
        mock_gc.create_requisition.return_value = AsyncMock(return_value={
            'link': 'https://ob.gocardless.com/psd2/start/req123',
            'requisition_id': 'req123'
        })

        with patch('app.api.routers.bank.get_active_provider', return_value='gocardless'):
            response = client.post(
                "/api/bank/connect",
                params={"institution_id": "BARCLAYS_BARCGB22"}
            )

            assert response.status_code == 200
            data = response.json()
            assert 'auth_link' in data
            assert 'requisition_id' in data

    @patch('app.api.routers.bank.plaid_service')
    def test_exchange_public_token(self, mock_plaid):
        """Test POST /bank/token/exchange"""
        mock_plaid.exchange_public_token.return_value = AsyncMock(return_value={
            'access_token': 'access-sandbox-token',
            'item_id': 'item123'
        })

        response = client.post(
            "/api/bank/token/exchange",
            json={"public_token": "public-sandbox-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'item_id' in data

    def test_get_transactions_not_connected(self):
        """Test GET /bank/transactions when no account connected"""
        with patch('app.api.routers.bank.get_active_provider', return_value='plaid'):
            response = client.get("/api/bank/transactions")

            assert response.status_code == 400
            assert "no bank account connected" in response.json()["detail"].lower()

    @patch('app.api.routers.bank.plaid_service')
    def test_get_transactions_plaid(self, mock_plaid):
        """Test GET /bank/transactions with Plaid"""
        # Mock user with connected account
        def mock_user_with_account():
            user = User(
                id=1,
                email="test@example.com",
                name="Test User",
                currency="USD",
                preferred_language="en",
                obapi_provider_id="access-token-123",
                banking_id="item-123"
            )
            return user

        app.dependency_overrides[get_current_user] = mock_user_with_account

        mock_plaid.get_transactions.return_value = AsyncMock(return_value=[
            {
                'transaction_id': 'txn1',
                'account_id': 'acc1',
                'amount': 50.00,
                'currency': 'USD',
                'date': '2025-12-10',
                'name': 'Coffee Shop',
                'merchant_name': 'Starbucks',
                'category': [],
                'pending': False,
                'payment_channel': 'in_store'
            }
        ])

        with patch('app.api.routers.bank.get_active_provider', return_value='plaid'):
            response = client.get("/api/bank/transactions", params={"use_cache": False})

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

        # Restore mock
        app.dependency_overrides[get_current_user] = mock_current_user

    def test_import_transaction(self):
        """Test POST /bank/transactions/{id}/import"""
        response = client.post(
            "/api/bank/transactions/txn123/import",
            params={"category": "food"}
        )

        # Will return 404 since transaction not in cache
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

