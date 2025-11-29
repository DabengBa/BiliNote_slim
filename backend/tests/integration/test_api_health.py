"""
Integration tests for health check API endpoints.

Tests the /api/sys_health and /api/sys_check endpoints.
Requirements: 1.1, 1.2
"""
import pytest


class TestHealthCheckAPI:
    """Tests for system health check endpoints."""

    def test_sys_check_returns_success(self, client):
        """
        Test that /api/sys_check returns a success response.
        
        Requirements: 1.1 - System should respond to health check requests
        """
        response = client.get("/api/sys_check")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["msg"] == "success"

    def test_sys_health_returns_response(self, client):
        """
        Test that /api/sys_health returns a response with FFmpeg status.
        
        Requirements: 1.2 - Should return FFmpeg installation status
        Note: The actual FFmpeg check may succeed or fail depending on environment,
        but the endpoint should always return a valid response structure.
        """
        response = client.get("/api/sys_health")
        
        assert response.status_code == 200
        data = response.json()
        # Response should have standard structure
        assert "code" in data
        assert "msg" in data
        assert "data" in data
        # Either success (code=0) or error about FFmpeg (code=500)
        assert data["code"] in [0, 500]

    def test_sys_check_response_format(self, client):
        """
        Test that /api/sys_check returns proper JSON response format.
        
        Requirements: 1.1 - Response should follow standard format
        """
        response = client.get("/api/sys_check")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        assert "code" in data
        assert "msg" in data
        assert "data" in data
        
        # Verify types
        assert isinstance(data["code"], int)
        assert isinstance(data["msg"], str)

    def test_nonexistent_endpoint_returns_404(self, client):
        """
        Test that calling a non-existent endpoint returns 404.
        
        Requirements: 1.5 - Non-existent endpoints should return 404
        """
        response = client.get("/api/nonexistent_endpoint")
        
        assert response.status_code == 404
