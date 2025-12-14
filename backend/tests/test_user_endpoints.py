"""
Integration tests for new user endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

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
        hidden_friend_ids=[]
    )
    return user


app.dependency_overrides[get_current_user] = mock_current_user
client = TestClient(app)


class TestPushNotificationEndpoints:
    """Test push notification endpoints"""

    @patch('app.api.routers.user.push_service')
    def test_update_push_subscription(self, mock_push_service):
        """Test POST /users/push-subscription"""
        mock_push_service.register_subscription = AsyncMock(return_value=True)

        response = client.post(
            "/api/users/push-subscription",
            json={
                "subscription": '{"endpoint": "https://fcm.google.com/..."}'
            }
        )

        assert response.status_code == 204

    @patch('app.api.routers.user.push_service')
    def test_get_web_push_public_key(self, mock_push_service):
        """Test GET /users/push-public-key"""
        mock_push_service.get_public_key.return_value = "test-public-key-base64"

        response = client.get("/api/users/push-public-key")

        assert response.status_code == 200
        data = response.json()
        assert "publicKey" in data
        assert data["publicKey"] == "test-public-key-base64"


class TestInviteFriendEndpoint:
    """Test invite friend endpoint"""

    @patch('app.api.routers.user.email_service')
    def test_invite_friend_new_user(self, mock_email_service):
        """Test POST /users/invite with new user"""
        mock_email_service.send_invite_email = AsyncMock(return_value=True)

        response = client.post(
            "/api/users/invite",
            json={
                "email": "newuser@example.com",
                "send_invite_email": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "email" in data

    def test_invite_friend_no_email(self):
        """Test invite without sending email"""
        response = client.post(
            "/api/users/invite",
            json={
                "email": "friend2@example.com",
                "send_invite_email": False
            }
        )

        assert response.status_code == 200


class TestOwnExpensesEndpoint:
    """Test own expenses endpoint"""

    def test_get_own_expenses(self):
        """Test GET /users/expenses/own"""
        response = client.get("/api/users/expenses/own")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestBalanceWithFriendEndpoint:
    """Test balance with friend endpoint"""

    def test_get_balances_with_friend(self):
        """Test GET /users/balances/friend/{friend_id}"""
        response = client.get("/api/users/balances/friend/2")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestFeedbackEndpoint:
    """Test feedback endpoint"""

    @patch('app.services.email_service.email_service.send_feedback_email')
    def test_submit_feedback(self, mock_send_email):
        """Test POST /users/feedback"""
        mock_send_email.return_value = AsyncMock(return_value=True)

        response = client.post(
            "/api/users/feedback",
            json={"feedback": "This is my feedback about the app. It's great!"}
        )

        assert response.status_code == 204
        mock_send_email.assert_called_once()

    def test_submit_feedback_too_short(self):
        """Test feedback that's too short"""
        response = client.post(
            "/api/users/feedback",
            json={"feedback": "Too short"}
        )

        assert response.status_code == 400
        assert "at least 10 characters" in response.json()["detail"]


class TestHideUnhideFriend:
    """Test hide/unhide friend endpoints"""

    def test_hide_friend(self):
        """Test POST /users/hide-friend/{friend_id}"""
        response = client.post("/api/users/hide-friend/5")

        assert response.status_code == 204

    def test_unhide_friend(self):
        """Test POST /users/unhide-friend/{friend_id}"""
        # First hide a friend
        client.post("/api/users/hide-friend/6")

        # Then unhide
        response = client.post("/api/users/unhide-friend/6")

        assert response.status_code == 204


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

