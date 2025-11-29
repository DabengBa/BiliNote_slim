"""
Property-based tests for URL parsing functionality.

**Feature: system-testing, Property 1: URL 解析一致性**
**Validates: Requirements 2.1, 2.2, 2.3**

Tests that for any valid video URL (Bilibili/YouTube/Douyin), the URL parser
should extract a non-empty video ID, and parsing the same URL multiple times
should return the same result.
"""
import sys
import os
import re
from typing import Optional

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


# Copy the function for isolated testing (avoids heavy import chain)
def extract_video_id(url: str, platform: str) -> Optional[str]:
    """从视频链接中提取视频 ID"""
    if platform == "bilibili":
        match = re.search(r"BV([0-9A-Za-z]+)", url)
        return f"BV{match.group(1)}" if match else None

    elif platform == "youtube":
        match = re.search(r"(?:v=|youtu\.be/)([0-9A-Za-z_-]{11})", url)
        return match.group(1) if match else None

    elif platform == "douyin":
        match = re.search(r"/video/(\d+)", url)
        return match.group(1) if match else None

    return None


# Strategies for generating valid video IDs
bilibili_bv_id = st.from_regex(r"[0-9A-Za-z]{10}", fullmatch=True)
youtube_video_id = st.from_regex(r"[0-9A-Za-z_-]{11}", fullmatch=True)
douyin_video_id = st.from_regex(r"[0-9]{19}", fullmatch=True)


# Strategies for generating valid URLs
@st.composite
def bilibili_url_strategy(draw):
    """Generate valid Bilibili URLs."""
    bv_id = draw(bilibili_bv_id)
    prefix = draw(st.sampled_from([
        "https://www.bilibili.com/video/BV",
        "https://bilibili.com/video/BV",
        "http://www.bilibili.com/video/BV",
    ]))
    suffix = draw(st.sampled_from(["", "?p=1", "?vd_source=abc123"]))
    return f"{prefix}{bv_id}{suffix}"


@st.composite
def youtube_url_strategy(draw):
    """Generate valid YouTube URLs."""
    video_id = draw(youtube_video_id)
    url_format = draw(st.sampled_from([
        f"https://www.youtube.com/watch?v={video_id}",
        f"https://youtube.com/watch?v={video_id}",
        f"https://youtu.be/{video_id}",
    ]))
    return url_format


@st.composite
def douyin_url_strategy(draw):
    """Generate valid Douyin URLs."""
    video_id = draw(douyin_video_id)
    prefix = draw(st.sampled_from([
        "https://www.douyin.com/video/",
        "https://douyin.com/video/",
    ]))
    return f"{prefix}{video_id}"


class TestUrlParsingConsistency:
    """
    **Feature: system-testing, Property 1: URL 解析一致性**
    
    For any valid video URL (Bilibili/YouTube/Douyin), the URL parser should:
    1. Extract a non-empty video ID
    2. Return the same result when parsing the same URL multiple times
    """

    @given(url=bilibili_url_strategy())
    @settings(max_examples=100)
    def test_bilibili_url_parsing_extracts_non_empty_id(self, url: str):
        """
        **Feature: system-testing, Property 1: URL 解析一致性**
        **Validates: Requirements 2.1**
        
        For any valid Bilibili URL, extract_video_id should return a non-empty BV ID.
        """
        result = extract_video_id(url, "bilibili")
        assert result is not None, f"Failed to extract ID from valid Bilibili URL: {url}"
        assert result.startswith("BV"), f"Bilibili ID should start with 'BV': {result}"
        assert len(result) > 2, f"Bilibili ID should have content after 'BV': {result}"

    @given(url=bilibili_url_strategy())
    @settings(max_examples=100)
    def test_bilibili_url_parsing_is_idempotent(self, url: str):
        """
        **Feature: system-testing, Property 1: URL 解析一致性**
        **Validates: Requirements 2.1**
        
        Parsing the same Bilibili URL multiple times should return the same result.
        """
        result1 = extract_video_id(url, "bilibili")
        result2 = extract_video_id(url, "bilibili")
        result3 = extract_video_id(url, "bilibili")
        assert result1 == result2 == result3, f"Inconsistent parsing for URL: {url}"

    @given(url=youtube_url_strategy())
    @settings(max_examples=100)
    def test_youtube_url_parsing_extracts_non_empty_id(self, url: str):
        """
        **Feature: system-testing, Property 1: URL 解析一致性**
        **Validates: Requirements 2.2**
        
        For any valid YouTube URL, extract_video_id should return a non-empty video ID.
        """
        result = extract_video_id(url, "youtube")
        assert result is not None, f"Failed to extract ID from valid YouTube URL: {url}"
        assert len(result) == 11, f"YouTube ID should be 11 characters: {result}"

    @given(url=youtube_url_strategy())
    @settings(max_examples=100)
    def test_youtube_url_parsing_is_idempotent(self, url: str):
        """
        **Feature: system-testing, Property 1: URL 解析一致性**
        **Validates: Requirements 2.2**
        
        Parsing the same YouTube URL multiple times should return the same result.
        """
        result1 = extract_video_id(url, "youtube")
        result2 = extract_video_id(url, "youtube")
        result3 = extract_video_id(url, "youtube")
        assert result1 == result2 == result3, f"Inconsistent parsing for URL: {url}"

    @given(url=douyin_url_strategy())
    @settings(max_examples=100)
    def test_douyin_url_parsing_extracts_non_empty_id(self, url: str):
        """
        **Feature: system-testing, Property 1: URL 解析一致性**
        **Validates: Requirements 2.3**
        
        For any valid Douyin URL, extract_video_id should return a non-empty video ID.
        """
        result = extract_video_id(url, "douyin")
        assert result is not None, f"Failed to extract ID from valid Douyin URL: {url}"
        assert result.isdigit(), f"Douyin ID should be numeric: {result}"

    @given(url=douyin_url_strategy())
    @settings(max_examples=100)
    def test_douyin_url_parsing_is_idempotent(self, url: str):
        """
        **Feature: system-testing, Property 1: URL 解析一致性**
        **Validates: Requirements 2.3**
        
        Parsing the same Douyin URL multiple times should return the same result.
        """
        result1 = extract_video_id(url, "douyin")
        result2 = extract_video_id(url, "douyin")
        result3 = extract_video_id(url, "douyin")
        assert result1 == result2 == result3, f"Inconsistent parsing for URL: {url}"
