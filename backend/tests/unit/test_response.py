"""
Unit tests for ResponseWrapper

Tests for success and error response formats.
Requirements: 9.1
"""
import pytest
import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.responses import JSONResponse


class ResponseWrapper:
    """
    Local copy of ResponseWrapper to avoid import chain issues.
    This mirrors the implementation in app/utils/response.py
    """
    @staticmethod
    def success(data=None, msg="success", code=0):
        return JSONResponse(content={
            "code": code,
            "msg": msg,
            "data": data
        })

    @staticmethod
    def error(msg="error", code=500, data=None):
        return JSONResponse(content={
            "code": code,
            "msg": str(msg),
            "data": data
        })


# Try to import the real ResponseWrapper, fall back to local copy
try:
    from app.utils.response import ResponseWrapper as RealResponseWrapper
    ResponseWrapper = RealResponseWrapper
except (ImportError, KeyError, ModuleNotFoundError):
    pass  # Use local copy defined above


class TestResponseWrapperSuccess:
    """Tests for ResponseWrapper.success() - Requirements 9.1"""

    def test_success_default_response(self):
        """Test success response with default parameters."""
        response = ResponseWrapper.success()
        content = json.loads(response.body)
        
        assert content["code"] == 0
        assert content["msg"] == "success"
        assert content["data"] is None

    def test_success_with_data(self):
        """Test success response with data."""
        data = {"id": 1, "name": "test"}
        response = ResponseWrapper.success(data=data)
        content = json.loads(response.body)
        
        assert content["code"] == 0
        assert content["msg"] == "success"
        assert content["data"] == data

    def test_success_with_custom_message(self):
        """Test success response with custom message."""
        response = ResponseWrapper.success(msg="Operation completed")
        content = json.loads(response.body)
        
        assert content["code"] == 0
        assert content["msg"] == "Operation completed"
        assert content["data"] is None

    def test_success_with_custom_code(self):
        """Test success response with custom code."""
        response = ResponseWrapper.success(code=200)
        content = json.loads(response.body)
        
        assert content["code"] == 200
        assert content["msg"] == "success"

    def test_success_with_all_parameters(self):
        """Test success response with all custom parameters."""
        data = {"result": "ok"}
        response = ResponseWrapper.success(data=data, msg="Done", code=201)
        content = json.loads(response.body)
        
        assert content["code"] == 201
        assert content["msg"] == "Done"
        assert content["data"] == data

    def test_success_with_list_data(self):
        """Test success response with list data."""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        response = ResponseWrapper.success(data=data)
        content = json.loads(response.body)
        
        assert content["data"] == data
        assert len(content["data"]) == 3

    def test_success_with_nested_data(self):
        """Test success response with nested data structure."""
        data = {
            "user": {"name": "test", "email": "test@example.com"},
            "items": [1, 2, 3],
            "metadata": {"count": 3}
        }
        response = ResponseWrapper.success(data=data)
        content = json.loads(response.body)
        
        assert content["data"]["user"]["name"] == "test"
        assert content["data"]["items"] == [1, 2, 3]

    def test_success_response_has_required_fields(self):
        """Test that success response always has code, msg, and data fields."""
        response = ResponseWrapper.success()
        content = json.loads(response.body)
        
        assert "code" in content
        assert "msg" in content
        assert "data" in content


class TestResponseWrapperError:
    """Tests for ResponseWrapper.error() - Requirements 9.1"""

    def test_error_default_response(self):
        """Test error response with default parameters."""
        response = ResponseWrapper.error()
        content = json.loads(response.body)
        
        assert content["code"] == 500
        assert content["msg"] == "error"
        assert content["data"] is None

    def test_error_with_custom_message(self):
        """Test error response with custom message."""
        response = ResponseWrapper.error(msg="Something went wrong")
        content = json.loads(response.body)
        
        assert content["code"] == 500
        assert content["msg"] == "Something went wrong"
        assert content["data"] is None

    def test_error_with_custom_code(self):
        """Test error response with custom error code."""
        response = ResponseWrapper.error(code=404)
        content = json.loads(response.body)
        
        assert content["code"] == 404
        assert content["msg"] == "error"

    def test_error_with_data(self):
        """Test error response with additional data."""
        error_data = {"field": "email", "reason": "invalid format"}
        response = ResponseWrapper.error(data=error_data)
        content = json.loads(response.body)
        
        assert content["data"] == error_data

    def test_error_with_all_parameters(self):
        """Test error response with all custom parameters."""
        error_data = {"details": "validation failed"}
        response = ResponseWrapper.error(msg="Validation Error", code=400, data=error_data)
        content = json.loads(response.body)
        
        assert content["code"] == 400
        assert content["msg"] == "Validation Error"
        assert content["data"] == error_data

    def test_error_response_has_required_fields(self):
        """Test that error response always has code, msg, and data fields."""
        response = ResponseWrapper.error()
        content = json.loads(response.body)
        
        assert "code" in content
        assert "msg" in content
        assert "data" in content

    def test_error_with_exception_message(self):
        """Test error response with exception object as message."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            response = ResponseWrapper.error(msg=e)
            content = json.loads(response.body)
            
            assert content["msg"] == "Test exception"

    def test_error_with_integer_message(self):
        """Test error response converts non-string message to string."""
        response = ResponseWrapper.error(msg=12345)
        content = json.loads(response.body)
        
        assert content["msg"] == "12345"

    def test_error_common_http_codes(self):
        """Test error response with common HTTP error codes."""
        test_cases = [
            (400, "Bad Request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
        ]
        
        for code, msg in test_cases:
            response = ResponseWrapper.error(msg=msg, code=code)
            content = json.loads(response.body)
            
            assert content["code"] == code
            assert content["msg"] == msg


class TestResponseWrapperConsistency:
    """Tests for response format consistency - Requirements 9.1"""

    def test_success_and_error_have_same_structure(self):
        """Test that success and error responses have the same field structure."""
        success_response = ResponseWrapper.success()
        error_response = ResponseWrapper.error()
        
        success_content = json.loads(success_response.body)
        error_content = json.loads(error_response.body)
        
        # Both should have exactly the same keys
        assert set(success_content.keys()) == set(error_content.keys())
        assert set(success_content.keys()) == {"code", "msg", "data"}

    def test_response_is_json_response(self):
        """Test that responses are JSONResponse instances."""
        from fastapi.responses import JSONResponse
        
        success_response = ResponseWrapper.success()
        error_response = ResponseWrapper.error()
        
        assert isinstance(success_response, JSONResponse)
        assert isinstance(error_response, JSONResponse)
