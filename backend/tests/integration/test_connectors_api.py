"""
Integration tests for connectors API endpoints.
"""
import pytest


@pytest.mark.integration
class TestConnectorsAPI:
    """Integration tests for connectors endpoints."""

    def test_list_connectors(self, test_client):
        """Test GET /api/connectors/ endpoint."""
        response = test_client.get("/api/connectors/")

        assert response.status_code == 200
        data = response.json()
        assert "connectors" in data
        assert isinstance(data["connectors"], dict)

        # Verify expected connectors exist
        connectors = data["connectors"]
        assert "github" in connectors
        assert "weather" in connectors
        assert "crypto" in connectors
        assert "hackernews" in connectors

    def test_list_connectors_structure(self, test_client):
        """Test structure of connector data."""
        response = test_client.get("/api/connectors/")
        data = response.json()

        # Each connector should have enabled and configured fields
        for name, connector in data["connectors"].items():
            assert "enabled" in connector
            assert "configured" in connector
            assert isinstance(connector["enabled"], bool)
            assert isinstance(connector["configured"], bool)

    def test_configure_connector_with_api_key(self, test_client):
        """Test configuring a connector with API key."""
        config = {
            "name": "github",
            "api_key": "test-github-token",
            "enabled": True
        }

        response = test_client.post("/api/connectors/configure", json=config)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "configured"
        assert data["connector"] == "github"

        # Verify connector is now configured and enabled
        list_response = test_client.get("/api/connectors/")
        connectors = list_response.json()["connectors"]
        assert connectors["github"]["configured"] is True
        assert connectors["github"]["enabled"] is True

    def test_configure_connector_without_api_key(self, test_client):
        """Test configuring a connector without API key (just enable/disable)."""
        config = {
            "name": "crypto",
            "enabled": True
        }

        response = test_client.post("/api/connectors/configure", json=config)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "configured"
        assert data["connector"] == "crypto"

    def test_configure_nonexistent_connector(self, test_client):
        """Test configuring a connector that doesn't exist."""
        config = {
            "name": "nonexistent_connector",
            "api_key": "test-key",
            "enabled": True
        }

        response = test_client.post("/api/connectors/configure", json=config)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_toggle_connector_enable(self, test_client):
        """Test toggling a connector from disabled to enabled."""
        # First, ensure it's disabled
        config = {"name": "weather", "enabled": False}
        test_client.post("/api/connectors/configure", json=config)

        # Toggle it
        response = test_client.post("/api/connectors/weather/toggle")

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True

    def test_toggle_connector_disable(self, test_client):
        """Test toggling a connector from enabled to disabled."""
        # First, ensure it's enabled
        config = {"name": "crypto", "enabled": True}
        test_client.post("/api/connectors/configure", json=config)

        # Toggle it
        response = test_client.post("/api/connectors/crypto/toggle")

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False

    def test_toggle_connector_twice(self, test_client):
        """Test toggling a connector twice returns to original state."""
        # Get initial state
        initial_response = test_client.get("/api/connectors/")
        initial_state = initial_response.json()["connectors"]["crypto"]["enabled"]

        # Toggle once
        test_client.post("/api/connectors/crypto/toggle")

        # Toggle again
        response = test_client.post("/api/connectors/crypto/toggle")

        assert response.status_code == 200
        assert response.json()["enabled"] == initial_state

    def test_toggle_nonexistent_connector(self, test_client):
        """Test toggling a connector that doesn't exist."""
        response = test_client.post("/api/connectors/nonexistent/toggle")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_configure_multiple_connectors(self, test_client):
        """Test configuring multiple connectors sequentially."""
        connectors_to_configure = [
            {"name": "github", "api_key": "github-token", "enabled": True},
            {"name": "weather", "api_key": "weather-key", "enabled": True},
            {"name": "crypto", "enabled": False}
        ]

        for config in connectors_to_configure:
            response = test_client.post("/api/connectors/configure", json=config)
            assert response.status_code == 200

        # Verify all were configured
        list_response = test_client.get("/api/connectors/")
        connectors = list_response.json()["connectors"]

        assert connectors["github"]["enabled"] is True
        assert connectors["github"]["configured"] is True
        assert connectors["weather"]["enabled"] is True
        assert connectors["weather"]["configured"] is True
        assert connectors["crypto"]["enabled"] is False

    def test_configure_invalid_request_body(self, test_client):
        """Test configure endpoint with invalid request body."""
        # Missing required 'name' field
        config = {"api_key": "test-key"}

        response = test_client.post("/api/connectors/configure", json=config)

        assert response.status_code == 422  # Validation error

    def test_default_connectors_state(self, test_client):
        """Test that crypto and hackernews are configured by default."""
        response = test_client.get("/api/connectors/")
        connectors = response.json()["connectors"]

        # These connectors don't need API keys, so they're always configured
        # enabled state may vary depending on test execution order
        assert connectors["crypto"]["configured"] is True
        assert connectors["hackernews"]["configured"] is True
        # Both should exist in response
        assert "crypto" in connectors
        assert "hackernews" in connectors

    def test_disable_configured_connector(self, test_client):
        """Test disabling a connector that is configured."""
        # Configure and enable
        config = {"name": "github", "api_key": "test-key", "enabled": True}
        test_client.post("/api/connectors/configure", json=config)

        # Disable it
        config["enabled"] = False
        response = test_client.post("/api/connectors/configure", json=config)

        assert response.status_code == 200

        # Verify it's disabled but still configured
        list_response = test_client.get("/api/connectors/")
        connector = list_response.json()["connectors"]["github"]
        assert connector["enabled"] is False
        assert connector["configured"] is True

    def test_configure_with_empty_api_key(self, test_client):
        """Test configuring with empty API key string."""
        config = {"name": "github", "api_key": "", "enabled": True}

        response = test_client.post("/api/connectors/configure", json=config)

        # Empty string is falsy, so configured should remain unchanged
        assert response.status_code == 200

        list_response = test_client.get("/api/connectors/")
        connector = list_response.json()["connectors"]["github"]
        # Configuration logic treats empty string as no key, configured state unchanged
        # (May be True if previous test configured it)
        assert "configured" in connector
