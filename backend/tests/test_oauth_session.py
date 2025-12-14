"""
Tests for OAuth, session management, and additional auth endpoints
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
        preferred_language="en"
    )
    return user


app.dependency_overrides[get_current_user] = mock_current_user
client = TestClient(app)


class TestGoogleOAuth:
    """Test Google OAuth endpoints"""

    @patch('app.api.routers.auth.settings')
    def test_google_login_not_configured(self, mock_settings):
        """Test Google login when not configured"""
        mock_settings.GOOGLE_CLIENT_ID = None

        response = client.get("/api/auth/google")

        assert response.status_code == 501
        assert "not configured" in response.json()["detail"].lower()

    @patch('app.api.routers.auth.settings')
    def test_google_login_configured(self, mock_settings):
        """Test Google login URL generation"""
        mock_settings.GOOGLE_CLIENT_ID = "test-client-id"
        mock_settings.CORS_ORIGINS = ["http://localhost:3000"]

        response = client.get("/api/auth/google")

        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "accounts.google.com" in data["auth_url"]
        assert "redirect_uri" in data

    @patch('httpx.AsyncClient')
    @patch('app.api.routers.auth.settings')
    def test_google_callback_success(self, mock_settings, mock_client):
        """Test successful Google OAuth callback"""
        mock_settings.GOOGLE_CLIENT_ID = "test-client-id"
        mock_settings.GOOGLE_CLIENT_SECRET = "test-secret"
        mock_settings.CORS_ORIGINS = ["http://localhost:3000"]

        # Mock token exchange response
        token_response = MagicMock()
        token_response.status_code = 200
        token_response.json.return_value = {
            'access_token': 'google-access-token',
            'id_token': 'google-id-token'
        }

        # Mock userinfo response
        userinfo_response = MagicMock()
        userinfo_response.status_code = 200
        userinfo_response.json.return_value = {
            'email': 'newuser@gmail.com',
            'name': 'New User',
            'picture': 'https://example.com/pic.jpg',
            'id': 'google-user-id-123'
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = token_response
        mock_client_instance.get.return_value = userinfo_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        response = client.get("/api/auth/google/callback?code=test-auth-code")

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data


class TestSessionManagement:
    """Test session refresh and logout endpoints"""

    @patch('app.core.security.decode_token')
    def test_refresh_token_valid(self, mock_decode):
        """Test refreshing access token"""
        mock_decode.return_value = {
            'sub': '1',
            'type': 'refresh',
            'exp': 9999999999
        }

        response = client.post(
            "/api/auth/refresh?refresh_token=valid-refresh-token"
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @patch('app.core.security.decode_token')
    def test_refresh_token_invalid(self, mock_decode):
        """Test refresh with invalid token"""
        mock_decode.return_value = None

        response = client.post(
            "/api/auth/refresh?refresh_token=invalid-token"
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @patch('app.core.security.decode_token')
    def test_refresh_token_wrong_type(self, mock_decode):
        """Test refresh with access token (wrong type)"""
        mock_decode.return_value = {
            'sub': '1',
            'type': 'access',  # Should be 'refresh'
            'exp': 9999999999
        }

        response = client.post(
            "/api/auth/refresh?refresh_token=access-token"
        )

        assert response.status_code == 401

    def test_logout_success(self):
        """Test logout endpoint"""
        response = client.post("/api/auth/logout")

        assert response.status_code == 204


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

