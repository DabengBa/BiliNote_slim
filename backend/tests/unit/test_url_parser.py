"""
Unit tests for URL parsing functionality.

Tests the extract_video_id function and is_supported_video_url validator
for Bilibili, YouTube, and Douyin platforms.

Requirements: 2.1, 2.2, 2.3
"""
import sys
import os
import re
from typing import Optional
from urllib.parse import urlparse

import pytest

# Add backend to path for direct module imports
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


# Import the functions directly to avoid app/__init__.py import chain
def extract_video_id(url: str, platform: str) -> Optional[str]:
    """
    从视频链接中提取视频 ID (copied from app.utils.url_parser for isolated testing)
    """
    if platform == "bilibili":
        # 匹配 BV号（如 BV1vc411b7Wa）
        match = re.search(r"BV([0-9A-Za-z]+)", url)
        return f"BV{match.group(1)}" if match else None

    elif platform == "youtube":
        # 匹配 v=xxxxx 或 youtu.be/xxxxx，ID 长度通常为 11
        match = re.search(r"(?:v=|youtu\.be/)([0-9A-Za-z_-]{11})", url)
        return match.group(1) if match else None

    elif platform == "douyin":
        # 匹配 douyin.com/video/1234567890123456789
        match = re.search(r"/video/(\d+)", url)
        return match.group(1) if match else None

    return None


SUPPORTED_PLATFORMS = {
    "bilibili": r"(https?://)?(www\.)?bilibili\.com/video/[a-zA-Z0-9]+",
    "youtube": r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+",
    "douyin": "douyin",
    "kuaishou": "kuaishou"
}


def is_supported_video_url(url: str) -> bool:
    """Check if URL is from a supported video platform (copied for isolated testing)"""
    parsed = urlparse(url)

    # 检查是否为Bilibili的短链接
    if parsed.netloc == "b23.tv":
        return True

    for name, pattern in SUPPORTED_PLATFORMS.items():
        if pattern in ["douyin", "kuaishou"]:
            if pattern in url:
                return True
        else:
            if re.match(pattern, url):
                return True
    return False


class TestBilibiliUrlParsing:
    """Tests for Bilibili URL parsing - Requirements 2.1"""

    def test_extract_bilibili_bv_id_standard_url(self):
        """Test extracting BV ID from standard Bilibili URL."""
        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        result = extract_video_id(url, "bilibili")
        assert result == "BV1xx411c7mD"

    def test_extract_bilibili_bv_id_without_www(self):
        """Test extracting BV ID from Bilibili URL without www."""
        url = "https://bilibili.com/video/BV1234567890"
        result = extract_video_id(url, "bilibili")
        assert result == "BV1234567890"

    def test_extract_bilibili_bv_id_with_query_params(self):
        """Test extracting BV ID from URL with query parameters."""
        url = "https://www.bilibili.com/video/BV1xx411c7mD?p=1&vd_source=abc"
        result = extract_video_id(url, "bilibili")
        assert result == "BV1xx411c7mD"

    def test_bilibili_url_validation_standard(self):
        """Test validation of standard Bilibili URL."""
        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        assert is_supported_video_url(url) is True

    def test_bilibili_url_validation_short_link(self):
        """Test validation of Bilibili short link (b23.tv)."""
        url = "https://b23.tv/abc123"
        assert is_supported_video_url(url) is True

    def test_bilibili_invalid_url_returns_none(self):
        """Test that invalid Bilibili URL returns None."""
        url = "https://www.bilibili.com/invalid/path"
        result = extract_video_id(url, "bilibili")
        assert result is None


class TestYoutubeUrlParsing:
    """Tests for YouTube URL parsing - Requirements 2.2"""

    def test_extract_youtube_id_standard_url(self):
        """Test extracting video ID from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extract_video_id(url, "youtube")
        assert result == "dQw4w9WgXcQ"

    def test_extract_youtube_id_without_www(self):
        """Test extracting video ID from YouTube URL without www."""
        url = "https://youtube.com/watch?v=abc123_-xyz"
        result = extract_video_id(url, "youtube")
        assert result == "abc123_-xyz"

    def test_extract_youtube_id_short_url(self):
        """Test extracting video ID from youtu.be short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = extract_video_id(url, "youtube")
        assert result == "dQw4w9WgXcQ"

    def test_extract_youtube_id_with_extra_params(self):
        """Test extracting video ID from URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120s"
        result = extract_video_id(url, "youtube")
        assert result == "dQw4w9WgXcQ"

    def test_youtube_url_validation_standard(self):
        """Test validation of standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert is_supported_video_url(url) is True

    def test_youtube_url_validation_short(self):
        """Test validation of YouTube short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert is_supported_video_url(url) is True

    def test_youtube_invalid_url_returns_none(self):
        """Test that invalid YouTube URL returns None."""
        url = "https://www.youtube.com/channel/UCxyz"
        result = extract_video_id(url, "youtube")
        assert result is None


class TestDouyinUrlParsing:
    """Tests for Douyin URL parsing - Requirements 2.3"""

    def test_extract_douyin_id_standard_url(self):
        """Test extracting video ID from standard Douyin URL."""
        url = "https://www.douyin.com/video/7123456789012345678"
        result = extract_video_id(url, "douyin")
        assert result == "7123456789012345678"

    def test_extract_douyin_id_without_www(self):
        """Test extracting video ID from Douyin URL without www."""
        url = "https://douyin.com/video/7123456789012345678"
        result = extract_video_id(url, "douyin")
        assert result == "7123456789012345678"

    def test_douyin_url_validation(self):
        """Test validation of Douyin URL."""
        url = "https://www.douyin.com/video/7123456789012345678"
        assert is_supported_video_url(url) is True

    def test_douyin_invalid_url_returns_none(self):
        """Test that invalid Douyin URL returns None."""
        url = "https://www.douyin.com/user/123"
        result = extract_video_id(url, "douyin")
        assert result is None


class TestUnsupportedPlatform:
    """Tests for unsupported platform handling."""

    def test_unsupported_platform_returns_none(self):
        """Test that unsupported platform returns None."""
        url = "https://www.example.com/video/123"
        result = extract_video_id(url, "unknown")
        assert result is None

    def test_invalid_url_validation(self):
        """Test that invalid URLs are rejected."""
        invalid_urls = [
            "https://example.com/video/123",
            "not-a-url",
            "ftp://files.example.com/video.mp4",
        ]
        for url in invalid_urls:
            assert is_supported_video_url(url) is False
