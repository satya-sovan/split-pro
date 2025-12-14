"""
Tests for push notification service
"""
import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from sqlalchemy.orm import Session

from app.services.push_service import PushNotificationService, push_service
from app.models.models import PushNotification


@pytest.fixture
def mock_db():
    """Mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def push_svc():
    """Push notification service instance"""
    svc = PushNotificationService()
    svc.vapid_private_key = "test-private-key"
    svc.vapid_public_key = "test-public-key"
    return svc


class TestPushNotificationService:
    """Test push notification service"""

    @pytest.mark.asyncio
    async def test_send_notification_no_subscription(self, push_svc, mock_db):
        """Test sending notification when user has no subscription"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = await push_svc.send_notification(
            mock_db,
            user_id=1,
            title="Test",
            body="Test notification"
        )

        assert result is False

    @pytest.mark.asyncio
    @patch('app.services.push_service.webpush')
    async def test_send_notification_success(self, mock_webpush, push_svc, mock_db):
        """Test successfully sending notification"""
        subscription_data = json.dumps({
            "endpoint": "https://fcm.googleapis.com/fcm/send/...",
            "keys": {
                "p256dh": "test-key",
                "auth": "test-auth"
            }
        })

        mock_subscription = MagicMock(spec=PushNotification)
        mock_subscription.subscription = subscription_data
        mock_db.query.return_value.filter.return_value.first.return_value = mock_subscription

        mock_webpush.return_value = None

        result = await push_svc.send_notification(
            mock_db,
            user_id=1,
            title="Test Title",
            body="Test Body",
            data={"expense_id": "123"}
        )

        assert result is True
        mock_webpush.assert_called_once()

        # Verify payload
        call_args = mock_webpush.call_args
        assert "subscription_info" in call_args.kwargs
        assert "data" in call_args.kwargs

        payload = json.loads(call_args.kwargs["data"])
        assert payload["title"] == "Test Title"
        assert payload["body"] == "Test Body"
        assert payload["data"]["expense_id"] == "123"

    @pytest.mark.asyncio
    @patch('app.services.push_service.webpush')
    async def test_send_notification_invalid_subscription(self, mock_webpush, push_svc, mock_db):
        """Test handling invalid subscription (410 Gone)"""
        from pywebpush import WebPushException

        subscription_data = json.dumps({"endpoint": "https://test.com"})
        mock_subscription = MagicMock(spec=PushNotification)
        mock_subscription.subscription = subscription_data
        mock_db.query.return_value.filter.return_value.first.return_value = mock_subscription

        # Simulate 410 Gone error
        mock_response = MagicMock()
        mock_response.status_code = 410
        error = WebPushException("Gone")
        error.response = mock_response
        mock_webpush.side_effect = error

        result = await push_svc.send_notification(
            mock_db,
            user_id=1,
            title="Test",
            body="Test"
        )

        assert result is False
        mock_db.delete.assert_called_once()  # Should delete invalid subscription

    @pytest.mark.asyncio
    async def test_register_subscription_new(self, push_svc, mock_db):
        """Test registering new push subscription"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        subscription_json = json.dumps({"endpoint": "https://test.com"})

        result = await push_svc.register_subscription(
            mock_db,
            user_id=1,
            subscription=subscription_json
        )

        assert result is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_subscription_update(self, push_svc, mock_db):
        """Test updating existing subscription"""
        existing = MagicMock(spec=PushNotification)
        existing.subscription = '{"old": "subscription"}'
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        new_subscription = json.dumps({"new": "subscription"})

        result = await push_svc.register_subscription(
            mock_db,
            user_id=1,
            subscription=new_subscription
        )

        assert result is True
        assert existing.subscription == new_subscription
        mock_db.add.assert_not_called()  # Should update, not add
        mock_db.commit.assert_called_once()

    def test_get_public_key(self, push_svc):
        """Test getting VAPID public key"""
        key = push_svc.get_public_key()
        assert key == "test-public-key"

    def test_get_public_key_not_configured(self):
        """Test getting public key when not configured"""
        svc = PushNotificationService()
        svc.vapid_public_key = None

        key = svc.get_public_key()
        assert key == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

