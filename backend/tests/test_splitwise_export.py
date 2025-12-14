"""
Tests for Splitwise import and data export
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from app.main import app
from app.api.deps import get_current_user
from app.models.models import User


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


class TestDataExport:
    """Test data export endpoint"""

    def test_export_user_data(self):
        """Test exporting all user data"""
        response = client.get("/api/users/data/export")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "user" in data
        assert "expenses" in data
        assert "groups" in data
        assert "balances" in data
        assert "export_date" in data
        assert "format_version" in data

        # Verify user data
        assert data["user"]["id"] == 1
        assert data["user"]["email"] == "test@example.com"

        # Should be lists (even if empty)
        assert isinstance(data["expenses"], list)
        assert isinstance(data["groups"], list)
        assert isinstance(data["balances"], list)


class TestSplitwiseImport:
    """Test Splitwise import endpoint"""

    @patch('app.api.routers.user.splitwise_import_service')
    def test_import_splitwise_data_success(self, mock_service):
        """Test successful Splitwise import"""
        # Create a coroutine that returns the stats dict
        async def mock_import(*args, **kwargs):
            return {
                'groups_imported': 2,
                'friends_imported': 5,
                'balances_imported': 10,
                'expenses_imported': 0,
                'errors': []
            }

        mock_service.import_groups_and_balances = mock_import

        splitwise_data = {
            "groups": [
                {
                    "id": 123,
                    "name": "Apartment",
                    "currency": "USD",
                    "members": [
                        {"email": "user1@example.com", "first_name": "User 1"}
                    ]
                }
            ],
            "friends": [
                {
                    "email": "friend@example.com",
                    "first_name": "Friend",
                    "balances": [
                        {"amount": "50.00", "currency_code": "USD"}
                    ]
                }
            ]
        }

        response = client.post(
            "/api/users/import/splitwise",
            json=splitwise_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "statistics" in data
        assert data["statistics"]["groups_imported"] == 2
        assert data["statistics"]["friends_imported"] == 5

    @patch('app.api.routers.user.splitwise_import_service')
    def test_import_splitwise_data_with_errors(self, mock_service):
        """Test Splitwise import with some errors"""
        async def mock_import(*args, **kwargs):
            return {
                'groups_imported': 1,
                'friends_imported': 3,
                'balances_imported': 5,
                'expenses_imported': 0,
                'errors': [
                    'Group "Invalid Group": Missing currency',
                    'Friend "invalid@email": Balance conversion error'
                ]
            }

        mock_service.import_groups_and_balances = mock_import

        response = client.post(
            "/api/users/import/splitwise",
            json={"groups": [], "friends": []}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["statistics"]["errors"]) == 2

    def test_import_splitwise_empty_data(self):
        """Test import with empty data"""
        response = client.post(
            "/api/users/import/splitwise",
            json={"groups": [], "friends": []}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestSplitwiseImportService:
    """Test Splitwise import service directly"""

    @pytest.mark.asyncio
    async def test_import_group_with_members(self):
        """Test importing a group with members"""
        from app.services.splitwise_import_service import splitwise_import_service
        from unittest.mock import MagicMock

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        group_data = {
            "id": 123,
            "name": "Test Group",
            "currency": "USD",
            "simplify_by_default": True,
            "members": [
                {
                    "email": "member1@example.com",
                    "first_name": "Member 1"
                },
                {
                    "email": "member2@example.com",
                    "first_name": "Member 2"
                }
            ],
            "balances": []
        }

        stats = {
            'groups_imported': 0,
            'friends_imported': 0,
            'balances_imported': 0,
            'expenses_imported': 0,
            'errors': []
        }

        await splitwise_import_service._import_group(
            mock_db,
            user_id=1,
            group_data=group_data,
            stats=stats
        )

        # Should have added group
        assert stats['groups_imported'] > 0

    @pytest.mark.asyncio
    async def test_import_friend_balance(self):
        """Test importing friend with balance"""
        from app.services.splitwise_import_service import splitwise_import_service
        from unittest.mock import MagicMock

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        friend_data = {
            "email": "friend@example.com",
            "first_name": "Friend Name",
            "default_currency": "EUR",
            "balances": [
                {
                    "amount": "25.50",
                    "currency_code": "EUR"
                }
            ]
        }

        stats = {
            'groups_imported': 0,
            'friends_imported': 0,
            'balances_imported': 0,
            'expenses_imported': 0,
            'errors': []
        }

        await splitwise_import_service._import_friend_balance(
            mock_db,
            user_id=1,
            friend_data=friend_data,
            stats=stats
        )

        # Should have added friend and balance
        assert stats['friends_imported'] > 0
        assert stats['balances_imported'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

