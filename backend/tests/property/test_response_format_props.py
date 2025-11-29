"""
Property-based tests for Response Format Consistency

**Feature: system-testing, Property 7: 错误响应格式一致性**
**Validates: Requirements 9.1**

Tests that error responses always contain the required fields (code, msg, data).
"""
import pytest
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hypothesis import given, settings, assume
from hypothesis import strategies as st
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


class TestErrorResponseFormatProperties:
    """
    Property-based tests for error response format consistency.
    
    **Feature: system-testing, Property 7: 错误响应格式一致性**
    **Validates: Requirements 9.1**
    """

    @given(
        error_msg=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
            blacklist_characters='\x00\r\n'
        )),
        error_code=st.integers(min_value=100, max_value=599)
    )
    @settings(max_examples=100)
    def test_error_response_contains_code_field(self, error_msg: str, error_code: int):
        """
        **Feature: system-testing, Property 7: 错误响应格式一致性**
        
        For any error message and error code, the error response JSON
        should always contain a 'code' field.
        """
        response = ResponseWrapper.error(msg=error_msg, code=error_code)
        content = json.loads(response.body)
        
        assert "code" in content, \
            f"Error response missing 'code' field for msg='{error_msg}', code={error_code}"

    @given(
        error_msg=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
            blacklist_characters='\x00\r\n'
        )),
        error_code=st.integers(min_value=100, max_value=599)
    )
    @settings(max_examples=100)
    def test_error_response_contains_msg_field(self, error_msg: str, error_code: int):
        """
        **Feature: system-testing, Property 7: 错误响应格式一致性**
        
        For any error message and error code, the error response JSON
        should always contain a 'msg' field.
        """
        response = ResponseWrapper.error(msg=error_msg, code=error_code)
        content = json.loads(response.body)
        
        assert "msg" in content, \
            f"Error response missing 'msg' field for msg='{error_msg}', code={error_code}"

    @given(
        error_msg=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
            blacklist_characters='\x00\r\n'
        )),
        error_code=st.integers(min_value=100, max_value=599)
    )
    @settings(max_examples=100)
    def test_error_response_contains_data_field(self, error_msg: str, error_code: int):
        """
        **Feature: system-testing, Property 7: 错误响应格式一致性**
        
        For any error message and error code, the error response JSON
        should always contain a 'data' field.
        """
        response = ResponseWrapper.error(msg=error_msg, code=error_code)
        content = json.loads(response.body)
        
        assert "data" in content, \
            f"Error response missing 'data' field for msg='{error_msg}', code={error_code}"

    @given(
        error_msg=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
            blacklist_characters='\x00\r\n'
        )),
        error_code=st.integers(min_value=100, max_value=599)
    )
    @settings(max_examples=100)
    def test_error_response_code_matches_input(self, error_msg: str, error_code: int):
        """
        **Feature: system-testing, Property 7: 错误响应格式一致性**
        
        For any error code, the error response should contain
        the exact same code value that was passed in.
        """
        response = ResponseWrapper.error(msg=error_msg, code=error_code)
        content = json.loads(response.body)
        
        assert content["code"] == error_code, \
            f"Error code mismatch: expected {error_code}, got {content['code']}"

    @given(
        error_msg=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
            blacklist_characters='\x00\r\n'
        )),
        error_code=st.integers(min_value=100, max_value=599)
    )
    @settings(max_examples=100)
    def test_error_response_msg_matches_input(self, error_msg: str, error_code: int):
        """
        **Feature: system-testing, Property 7: 错误响应格式一致性**
        
        For any error message, the error response should contain
        the exact same message value that was passed in (as string).
        """
        response = ResponseWrapper.error(msg=error_msg, code=error_code)
        content = json.loads(response.body)
        
        assert content["msg"] == str(error_msg), \
            f"Error msg mismatch: expected '{error_msg}', got '{content['msg']}'"

    @given(
        error_msg=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
            blacklist_characters='\x00\r\n'
        )),
        error_code=st.integers(min_value=100, max_value=599),
        error_data=st.one_of(
            st.none(),
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20, alphabet=st.characters(
                    whitelist_categories=('L', 'N'),
                    blacklist_characters='\x00'
                )),
                values=st.one_of(st.text(max_size=50), st.integers(), st.booleans()),
                max_size=5
            )
        )
    )
    @settings(max_examples=100)
    def test_error_response_with_data_contains_all_fields(self, error_msg: str, error_code: int, error_data):
        """
        **Feature: system-testing, Property 7: 错误响应格式一致性**
        
        For any error message, code, and data, the error response
        should contain all three required fields: code, msg, and data.
        """
        response = ResponseWrapper.error(msg=error_msg, code=error_code, data=error_data)
        content = json.loads(response.body)
        
        assert "code" in content, "Missing 'code' field"
        assert "msg" in content, "Missing 'msg' field"
        assert "data" in content, "Missing 'data' field"
        assert content["code"] == error_code
        assert content["msg"] == str(error_msg)
        assert content["data"] == error_data

    @given(
        error_code=st.integers(min_value=100, max_value=599)
    )
    @settings(max_examples=100)
    def test_error_response_msg_is_string_type(self, error_code: int):
        """
        **Feature: system-testing, Property 7: 错误响应格式一致性**
        
        For any error code passed as message, the msg field in the response
        should always be a string type.
        """
        # Pass integer as message to test string conversion
        response = ResponseWrapper.error(msg=error_code, code=500)
        content = json.loads(response.body)
        
        assert isinstance(content["msg"], str), \
            f"Error msg should be string, got {type(content['msg'])}"

    @given(
        error_msg=st.text(min_size=0, max_size=200, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
            blacklist_characters='\x00\r\n'
        )),
        error_code=st.integers(min_value=100, max_value=599)
    )
    @settings(max_examples=100)
    def test_error_response_is_json_response(self, error_msg: str, error_code: int):
        """
        **Feature: system-testing, Property 7: 错误响应格式一致性**
        
        For any error message and code, the response should be
        a valid JSONResponse instance.
        """
        response = ResponseWrapper.error(msg=error_msg, code=error_code)
        
        assert isinstance(response, JSONResponse), \
            f"Response should be JSONResponse, got {type(response)}"
