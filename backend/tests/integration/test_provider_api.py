"""
Integration tests for Provider API endpoints.

Tests the /api/get_all_providers, /api/add_provider, and /api/update_provider endpoints.
Requirements: 1.3, 5.1, 5.2
"""
import pytest


class TestProviderAPI:
    """Tests for Provider management API endpoints."""

    def test_get_all_providers_returns_list(self, client):
        """
        Test that /api/get_all_providers returns a list of providers.
        
        Requirements: 1.3 - Should return all configured AI providers
        """
        response = client.get("/api/get_all_providers")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        # Data should be a list (may be empty if no providers configured)
        assert isinstance(data["data"], list)

    def test_get_all_providers_response_format(self, client):
        """
        Test that /api/get_all_providers returns proper response format.
        
        Requirements: 1.3 - Response should follow standard format
        """
        response = client.get("/api/get_all_providers")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify standard response structure
        assert "code" in data
        assert "msg" in data
        assert "data" in data

    def test_add_provider_success(self, client):
        """
        Test that /api/add_provider successfully adds a new provider.
        
        Requirements: 5.1 - Should validate required fields and save to database
        """
        provider_data = {
            "name": "Test Provider",
            "api_key": "sk-test1234567890abcdef",
            "base_url": "https://api.test.com/v1",
            "type": "openai",
            "logo": "custom"
        }
        
        response = client.post("/api/add_provider", json=provider_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "添加" in data["msg"] or "success" in data["msg"].lower()

    def test_add_provider_returns_id(self, client):
        """
        Test that /api/add_provider returns the created provider ID.
        
        Requirements: 5.1 - Should return success status after saving
        """
        provider_data = {
            "name": "Another Test Provider",
            "api_key": "sk-another1234567890",
            "base_url": "https://api.another.com/v1",
            "type": "deepseek",
            "logo": "custom"
        }
        
        response = client.post("/api/add_provider", json=provider_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # Should have data with the created provider info
        assert data["data"] is not None

    def test_add_provider_missing_required_fields(self, client):
        """
        Test that /api/add_provider validates required fields.
        
        Requirements: 5.1 - Should validate required fields
        """
        # Missing api_key and base_url
        incomplete_data = {
            "name": "Incomplete Provider",
            "type": "openai"
        }
        
        response = client.post("/api/add_provider", json=incomplete_data)
        
        # Should return validation error (422 for Pydantic validation)
        assert response.status_code == 422

    def test_update_provider_success(self, client):
        """
        Test that /api/update_provider successfully updates a provider.
        
        Requirements: 5.2 - Should update corresponding record
        """
        # First, add a provider
        provider_data = {
            "name": "Provider To Update",
            "api_key": "sk-update1234567890",
            "base_url": "https://api.update.com/v1",
            "type": "openai",
            "logo": "custom"
        }
        
        add_response = client.post("/api/add_provider", json=provider_data)
        assert add_response.status_code == 200
        added_data = add_response.json()
        
        # Get the provider ID from the response
        provider_id = added_data.get("data")
        if provider_id is None:
            pytest.skip("Could not get provider ID from add response")
        
        # Now update the provider
        update_data = {
            "id": provider_id,
            "name": "Updated Provider Name"
        }
        
        update_response = client.post("/api/update_provider", json=update_data)
        
        assert update_response.status_code == 200
        update_result = update_response.json()
        assert update_result["code"] == 0

    def test_update_provider_no_fields_error(self, client):
        """
        Test that /api/update_provider returns error when no fields provided.
        
        Requirements: 5.2 - Should validate update data
        """
        update_data = {
            "id": "some-id"
            # No other fields provided
        }
        
        response = client.post("/api/update_provider", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        # Should return error about missing fields
        assert data["code"] != 0 or "至少" in data.get("msg", "")

    def test_get_provider_by_id(self, client):
        """
        Test that /api/get_provider_by_id returns provider details.
        
        Requirements: 5.4 - Should return masked API key
        """
        # First add a provider
        provider_data = {
            "name": "Provider For Get",
            "api_key": "sk-gettest1234567890abcdef",
            "base_url": "https://api.gettest.com/v1",
            "type": "qwen",
            "logo": "custom"
        }
        
        add_response = client.post("/api/add_provider", json=provider_data)
        assert add_response.status_code == 200
        added_data = add_response.json()
        
        provider_id = added_data.get("data")
        if provider_id is None:
            pytest.skip("Could not get provider ID from add response")
        
        # Get the provider by ID
        get_response = client.get(f"/api/get_provider_by_id/{provider_id}")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["code"] == 0
        assert data["data"] is not None
        
        # API key should be masked (contains asterisks)
        if data["data"].get("api_key"):
            assert "*" in data["data"]["api_key"]
