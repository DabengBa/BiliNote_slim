"""
Property-based tests for invalid URL rejection.

**Feature: system-testing, Property 2: 无效 URL 拒绝**
**Validates: Requirements 2.4**

Tests that for any URL that doesn't match supported platform formats,
the URL validator should return False.
"""
import sys
import os
import re
from urllib.parse import urlparse

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


# Copy the validation function for isolated testing
SUPPORTED_PLATFORMS = {
    "bilibili": r"(https?://)?(www\.)?bilibili\.com/video/[a-zA-Z0-9]+",
    "youtube": r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+",
    "douyin": "douyin",
    "kuaishou": "kuaishou"
}


def is_supported_video_url(url: str) -> bool:
    """Check if URL is from a supported video platform."""
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


# Strategy for generating URLs that are definitely NOT from supported platforms
@st.composite
def unsupported_url_strategy(draw):
    """Generate URLs that are definitely not from supported video platforms."""
    # Generate random domain that is NOT a supported platform
    unsupported_domains = [
        "example.com",
        "test.org",
        "random-site.net",
        "vimeo.com",
        "dailymotion.com",
        "twitch.tv",
        "facebook.com",
        "twitter.com",
        "instagram.com",
        "tiktok.com",  # Note: different from douyin
    ]
    
    domain = draw(st.sampled_from(unsupported_domains))
    path = draw(st.from_regex(r"/[a-z0-9/]{0,30}", fullmatch=True))
    protocol = draw(st.sampled_from(["https://", "http://"]))
    
    return f"{protocol}{domain}{path}"


@st.composite
def malformed_url_strategy(draw):
    """Generate malformed or invalid URLs."""
    malformed_patterns = [
        # Missing protocol
        draw(st.from_regex(r"www\.[a-z]{3,10}\.[a-z]{2,3}/[a-z0-9]{0,10}", fullmatch=True)),
        # Just text, not a URL
        draw(st.from_regex(r"[a-z]{5,20}", fullmatch=True)),
        # Invalid protocol
        f"ftp://{draw(st.from_regex(r'[a-z]{3,10}', fullmatch=True))}.com/video",
        # Empty or whitespace
        "",
        "   ",
    ]
    return draw(st.sampled_from(malformed_patterns))


@st.composite
def partial_match_url_strategy(draw):
    """Generate URLs that partially match but are not valid supported URLs."""
    partial_patterns = [
        # Bilibili-like but wrong path
        f"https://www.bilibili.com/user/{draw(st.from_regex(r'[0-9]{5,10}', fullmatch=True))}",
        f"https://www.bilibili.com/bangumi/{draw(st.from_regex(r'[0-9]{5,10}', fullmatch=True))}",
        # YouTube-like but wrong format
        f"https://www.youtube.com/channel/{draw(st.from_regex(r'[A-Za-z0-9]{10,20}', fullmatch=True))}",
        f"https://www.youtube.com/playlist?list={draw(st.from_regex(r'[A-Za-z0-9]{10,20}', fullmatch=True))}",
        # Random video-like paths on wrong domains
        f"https://www.example.com/video/{draw(st.from_regex(r'[0-9]{10,15}', fullmatch=True))}",
    ]
    return draw(st.sampled_from(partial_patterns))


class TestInvalidUrlRejection:
    """
    **Feature: system-testing, Property 2: 无效 URL 拒绝**
    
    For any URL that doesn't match supported platform formats,
    the URL validator should return False.
    """

    @given(url=unsupported_url_strategy())
    @settings(max_examples=100)
    def test_unsupported_domain_urls_are_rejected(self, url: str):
        """
        **Feature: system-testing, Property 2: 无效 URL 拒绝**
        **Validates: Requirements 2.4**
        
        URLs from unsupported domains should be rejected.
        """
        result = is_supported_video_url(url)
        assert result is False, f"Unsupported URL should be rejected: {url}"

    @given(url=malformed_url_strategy())
    @settings(max_examples=100)
    def test_malformed_urls_are_rejected(self, url: str):
        """
        **Feature: system-testing, Property 2: 无效 URL 拒绝**
        **Validates: Requirements 2.4**
        
        Malformed or invalid URLs should be rejected.
        """
        result = is_supported_video_url(url)
        assert result is False, f"Malformed URL should be rejected: {url}"

    @given(url=partial_match_url_strategy())
    @settings(max_examples=100)
    def test_partial_match_urls_are_rejected(self, url: str):
        """
        **Feature: system-testing, Property 2: 无效 URL 拒绝**
        **Validates: Requirements 2.4**
        
        URLs that partially match supported platforms but are not valid video URLs
        should be rejected.
        """
        result = is_supported_video_url(url)
        assert result is False, f"Partial match URL should be rejected: {url}"

    @given(random_text=st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_random_text_is_rejected(self, random_text: str):
        """
        **Feature: system-testing, Property 2: 无效 URL 拒绝**
        **Validates: Requirements 2.4**
        
        Random text that is not a valid URL should be rejected,
        unless it accidentally contains a supported platform keyword.
        """
        # Skip if the random text accidentally contains supported platform keywords
        assume("bilibili.com/video/" not in random_text)
        assume("youtube.com/watch?v=" not in random_text)
        assume("youtu.be/" not in random_text)
        assume("douyin" not in random_text)
        assume("kuaishou" not in random_text)
        assume("b23.tv" not in random_text)
        
        result = is_supported_video_url(random_text)
        assert result is False, f"Random text should be rejected: {random_text}"
