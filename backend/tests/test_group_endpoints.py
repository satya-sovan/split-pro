"""
Integration tests for new group endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

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


class TestGroupTotalsEndpoint:
    """Test group totals endpoint"""

    def test_get_group_totals(self):
        """Test GET /groups/{group_id}/totals"""
        # This will fail without a real group, but tests the endpoint structure
        response = client.get("/api/groups/999/totals")

        # Should return 403 or 404 for non-existent group
        assert response.status_code in [403, 404]


class TestDeleteGroupEndpoint:
    """Test delete group endpoint"""

    def test_delete_group(self):
        """Test DELETE /groups/{group_id}"""
        response = client.delete("/api/groups/999")

        # Should return 404 for non-existent group
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGroupsWithBalancesEndpoint:
    """Test groups with balances endpoint"""

    def test_get_groups_with_balances(self):
        """Test GET /groups/with-balances"""
        response = client.get("/api/groups/with-balances")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_groups_with_balances_include_archived(self):
        """Test getting groups including archived ones"""
        response = client.get(
            "/api/groups/with-balances",
            params={"include_archived": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_groups_with_balances_structure(self):
        """Test the response structure includes balances"""
        response = client.get("/api/groups/with-balances")

        assert response.status_code == 200
        data = response.json()

        # If there are groups, verify structure
        if len(data) > 0:
            group = data[0]
            assert "id" in group
            assert "name" in group
            assert "balances" in group
            assert "latest_expense_at" in group
            assert isinstance(group["balances"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

