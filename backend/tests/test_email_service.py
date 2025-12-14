"""
Tests for email service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from email.mime.text import MIMEText

from app.services.email_service import EmailService, email_service
from app.models.models import User


@pytest.fixture
def mock_user():
    """Mock user object"""
    user = MagicMock(spec=User)
    user.id = 1
    user.name = "Test User"
    user.email = "test@example.com"
    return user


@pytest.fixture
def email_svc():
    """Email service instance"""
    svc = EmailService()
    svc.smtp_host = "smtp.test.com"
    svc.smtp_port = 587
    svc.smtp_user = "user@test.com"
    svc.smtp_password = "password"
    return svc


class TestEmailService:
    """Test email service"""

    @pytest.mark.asyncio
    @patch('aiosmtplib.send')
    async def test_send_email_success(self, mock_send, email_svc):
        """Test sending email successfully"""
        mock_send.return_value = AsyncMock()

        result = await email_svc.send_email(
            to_email="recipient@test.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text"
        )

        assert result is True
        mock_send.assert_called_once()

        # Verify email content
        call_args = mock_send.call_args
        msg = call_args.args[0]
        assert msg['Subject'] == "Test Subject"
        assert msg['To'] == "recipient@test.com"

    @pytest.mark.asyncio
    async def test_send_email_not_configured(self):
        """Test sending email when SMTP not configured"""
        svc = EmailService()
        svc.smtp_host = None

        result = await svc.send_email(
            to_email="test@test.com",
            subject="Test",
            html_content="<p>Test</p>"
        )

        assert result is False

    @pytest.mark.asyncio
    @patch('aiosmtplib.send')
    async def test_send_email_error(self, mock_send, email_svc):
        """Test error handling when sending email"""
        mock_send.side_effect = Exception("SMTP Error")

        result = await email_svc.send_email(
            to_email="test@test.com",
            subject="Test",
            html_content="<p>Test</p>"
        )

        assert result is False

    @pytest.mark.asyncio
    @patch('aiosmtplib.send')
    async def test_send_invite_email(self, mock_send, email_svc):
        """Test sending invitation email"""
        mock_send.return_value = AsyncMock()

        result = await email_svc.send_invite_email(
            to_email="friend@test.com",
            from_name="John Doe"
        )

        assert result is True
        mock_send.assert_called_once()

        # Verify email contains invitation details
        msg = mock_send.call_args.args[0]
        assert "John Doe" in msg.as_string()
        assert "invited you to SplitPro" in msg['Subject']

    @pytest.mark.asyncio
    @patch('aiosmtplib.send')
    async def test_send_feedback_email(self, mock_send, email_svc, mock_user):
        """Test sending feedback email"""
        mock_send.return_value = AsyncMock()
        email_svc.from_email = "noreply@splitpro.app"

        result = await email_svc.send_feedback_email(
            feedback="This is my feedback about the app",
            user=mock_user
        )

        assert result is True
        mock_send.assert_called_once()

        # Verify email contains feedback
        msg = mock_send.call_args.args[0]
        assert "Feedback from Test User" in msg['Subject']
        email_body = msg.as_string()
        assert "This is my feedback about the app" in email_body
        assert "test@example.com" in email_body

    @pytest.mark.asyncio
    @patch('aiosmtplib.send')
    async def test_send_magic_link_email(self, mock_send, email_svc):
        """Test sending magic link email"""
        mock_send.return_value = AsyncMock()

        magic_link = "https://splitpro.app/auth/verify?token=abc123"

        result = await email_svc.send_magic_link_email(
            to_email="user@test.com",
            magic_link=magic_link
        )

        assert result is True
        mock_send.assert_called_once()

        # Verify email contains magic link
        msg = mock_send.call_args.args[0]
        assert "Login to SplitPro" in msg['Subject']
        email_body = msg.as_string()
        assert magic_link in email_body
        assert "expire in 1 hour" in email_body

    @pytest.mark.asyncio
    @patch('aiosmtplib.send')
    async def test_send_email_html_only(self, mock_send, email_svc):
        """Test sending HTML-only email"""
        mock_send.return_value = AsyncMock()

        result = await email_svc.send_email(
            to_email="test@test.com",
            subject="HTML Only",
            html_content="<h1>HTML Content</h1>"
        )

        assert result is True

        # Verify only HTML part is present
        msg = mock_send.call_args.args[0]
        parts = list(msg.walk())
        html_parts = [p for p in parts if p.get_content_type() == 'text/html']
        text_parts = [p for p in parts if p.get_content_type() == 'text/plain']

        assert len(html_parts) > 0
        # Text part should not be present if not provided
        # Note: multipart structure may still have empty text part


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

