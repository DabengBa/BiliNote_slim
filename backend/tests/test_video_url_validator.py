"""
测试视频URL验证器
"""
import pytest
from app.validators.video_url_validator import is_supported_video_url


class TestVideoUrlValidator:
    """测试URL验证功能"""

    def test_supported_bilibili_url(self):
        """测试支持的B站URL"""
        # 标准B站视频链接
        assert is_supported_video_url("https://www.bilibili.com/video/BV1xx411c7mA") is True
        # 无www的B站链接
        assert is_supported_video_url("https://bilibili.com/video/BV1xx411c7mA") is True
        # 不带协议的B站链接
        assert is_supported_video_url("www.bilibili.com/video/BV1xx411c7mA") is True

    def test_supported_bilibili_short_url(self):
        """测试B站短链接"""
        # B站短链接
        assert is_supported_video_url("https://b23.tv/abc123") is True
        # 不带协议的短链接
        assert is_supported_video_url("b23.tv/abc123") is True

    def test_supported_youtube_url(self):
        """测试支持的YouTube URL"""
        # 标准YouTube链接
        assert is_supported_video_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        # YouTube短链接
        assert is_supported_video_url("https://youtu.be/dQw4w9WgXcQ") is True
        # 无www的YouTube链接
        assert is_supported_video_url("https://youtube.com/watch?v=dQw4w9WgXcQ") is True

    def test_reject_douyin_url(self):
        """测试拒绝抖音URL - 验收标准1"""
        # 抖音域名应被拒绝
        assert is_supported_video_url("https://www.douyin.com/video/123456789") is False
        # 抖音短链接应被拒绝
        assert is_supported_video_url("https://v.douyin.com/abc123/") is False

    def test_reject_kuaishou_url(self):
        """测试拒绝快手URL - 验收标准1"""
        # 快手域名应被拒绝
        assert is_supported_video_url("https://www.kuaishou.com/video/123456") is False
        # 快手短链接应被拒绝
        assert is_supported_video_url("https://v.kuaishou.com/abc123/") is False

    def test_reject_xiaoyuzhou_url(self):
        """测试拒绝小宇宙URL - 验收标准1"""
        # 小宇宙域名应被拒绝
        assert is_supported_video_url("https://www.xiaoyuzhoufm.com/podcast/123") is False

    def test_reject_unsupported_platforms(self):
        """测试拒绝所有不支持的平台 - 验收标准5"""
        unsupported_urls = [
            "https://www.douyin.com/video/123",
            "https://v.douyin.com/abc/",
            "https://www.kuaishou.com/video/123",
            "https://v.kuaishou.com/abc/",
            "https://www.xiaoyuzhoufm.com/podcast/123",
            "https://www.tiktok.com/video/123",
            "https://www.instagram.com/p/123",
        ]

        for url in unsupported_urls:
            assert is_supported_video_url(url) is False, f"{url} should not be supported"
