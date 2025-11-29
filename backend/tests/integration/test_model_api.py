"""
Integration tests for Model API endpoints.

Tests the /api/model_list endpoint.
Requirements: 1.4
"""
import pytest


class TestModelAPI:
    """Tests for Model management API endpoints."""

    def test_model_list_returns_response(self, client):
        """
        Test that /api/model_list returns a valid response.
        
        Requirements: 1.4 - Should return all available models
        """
        response = client.get("/api/model_list")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data

    def test_model_list_response_format(self, client):
        """
        Test that /api/model_list returns proper response format.
        
        Requirements: 1.4 - Response should follow standard format
        """
        response = client.get("/api/model_list")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify standard response structure
        assert "code" in data
        assert "msg" in data
        assert "data" in data
        
        # Data should be a list
        assert isinstance(data["data"], list)

    def test_model_list_success_message(self, client):
        """
        Test that /api/model_list returns success message.
        
        Requirements: 1.4 - Should return success status
        """
        response = client.get("/api/model_list")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # Message should indicate success
        assert "成功" in data["msg"] or "success" in data["msg"].lower()

    def test_model_list_by_provider_nonexistent(self, client):
        """
        Test that /api/model_list/{provider_id} handles non-existent provider.
        
        Requirements: 1.4 - Should handle edge cases gracefully
        """
        response = client.get("/api/model_list/nonexistent-provider-id")
        
        assert response.status_code == 200
        data = response.json()
        # Should return empty list or error for non-existent provider
        assert "data" in data

    def test_model_enable_by_provider_nonexistent(self, client):
        """
        Test that /api/model_enable/{provider_id} handles non-existent provider.
        
        Requirements: 1.4 - Should handle edge cases gracefully
        """
        response = client.get("/api/model_enable/nonexistent-provider-id")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
