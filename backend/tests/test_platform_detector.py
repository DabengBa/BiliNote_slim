# backend/tests/test_platform_detector.py
"""
URL平台检测器单元测试
"""

import pytest
import asyncio
from app.utils.platform_detector import (
    PlatformDetector,
    PlatformInfo,
    detect_platform,
    is_supported_platform_url,
)


class TestPlatformDetector:
    """平台检测器测试类"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = PlatformDetector()
    
    def test_bilibili_main_format(self):
        """测试Bilibili主格式URL检测"""
        test_urls = [
            "https://www.bilibili.com/video/BV1xx411c7mT",
            "http://www.bilibili.com/video/BV1xx411c7mT",
            "www.bilibili.com/video/BV1xx411c7mT",
            "bilibili.com/video/BV1xx411c7mT",
        ]
        
        for url in test_urls:
            platform_info = self.detector.detect_platform(url)
            assert platform_info.platform == "bilibili"
            assert platform_info.confidence >= 0.9
            assert "domain" in platform_info.extra_info["detection_method"]
    
    def test_bilibili_short_url(self):
        """测试Bilibili短链接检测"""
        test_urls = [
            "https://b23.tv/BV1xx411c7mT",
            "http://b23.tv/BV1xx411c7mT",
            "b23.tv/BV1xx411c7mT",
        ]
        
        for url in test_urls:
            platform_info = self.detector.detect_platform(url)
            assert platform_info.platform == "bilibili"
            assert platform_info.confidence >= 0.9
    
    def test_youtube_main_format(self):
        """测试YouTube主格式URL检测"""
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "youtube.com/watch?v=dQw4w9WgXcQ",
        ]
        
        for url in test_urls:
            platform_info = self.detector.detect_platform(url)
            assert platform_info.platform == "youtube"
            assert platform_info.confidence >= 0.9
    
    def test_youtube_short_url(self):
        """测试YouTube短链接检测"""
        test_urls = [
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtu.be/dQw4w9WgXcQ",
            "youtu.be/dQw4w9WgXcQ",
        ]
        
        for url in test_urls:
            platform_info = self.detector.detect_platform(url)
            assert platform_info.platform == "youtube"
            assert platform_info.confidence >= 0.9
    
    def test_unsupported_url(self):
        """测试不支持的URL"""
        test_urls = [
            "https://vimeo.com/123456",
            "https://twitter.com/user/status/123",
            "https://example.com/video",
            "not-a-url",
            "",
        ]
        
        for url in test_urls:
            with pytest.raises(Exception):  # 应该抛出UnsupportedPlatformError或InvalidVideoURLError
                self.detector.detect_platform(url)
    
    def test_invalid_url_format(self):
        """测试无效URL格式"""
        test_urls = [
            "not-a-url",
            "",
            "ftp://example.com",
            "file:///local/file",
        ]
        
        for url in test_urls:
            with pytest.raises(Exception):
                self.detector.detect_platform(url)
    
    def test_get_supported_platforms(self):
        """测试获取支持的平台列表"""
        platforms = self.detector.get_supported_platforms()
        assert isinstance(platforms, list)
        assert "bilibili" in platforms
        assert "youtube" in platforms
        assert len(platforms) >= 2
    
    def test_is_supported_url(self):
        """测试便捷方法：检查URL是否支持"""
        # 支持的URL
        supported_urls = [
            "https://www.bilibili.com/video/BV1xx411c7mT",
            "https://youtu.be/dQw4w9WgXcQ",
            "b23.tv/test",
        ]
        
        for url in supported_urls:
            assert self.detector.is_supported_url(url) is True
        
        # 不支持的URL
        unsupported_urls = [
            "https://vimeo.com/123456",
            "not-a-url",
            "",
        ]
        
        for url in unsupported_urls:
            assert self.detector.is_supported_url(url) is False
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        # 测试detect_platform函数
        platform_info = detect_platform("https://www.bilibili.com/video/BV1xx411c7mT")
        assert isinstance(platform_info, PlatformInfo)
        assert platform_info.platform == "bilibili"
        
        # 测试is_supported_platform_url函数
        assert is_supported_platform_url("https://www.bilibili.com/video/BV1xx411c7mT") is True
        assert is_supported_platform_url("https://vimeo.com/123") is False
    
    def test_platform_info_structure(self):
        """测试PlatformInfo数据结构"""
        url = "https://www.bilibili.com/video/BV1xx411c7mT"
        platform_info = self.detector.detect_platform(url)
        
        assert isinstance(platform_info, PlatformInfo)
        assert hasattr(platform_info, 'platform')
        assert hasattr(platform_info, 'confidence')
        assert hasattr(platform_info, 'original_url')
        assert hasattr(platform_info, 'normalized_url')
        assert hasattr(platform_info, 'extra_info')
        
        assert platform_info.platform == "bilibili"
        assert 0.0 <= platform_info.confidence <= 1.0
        assert platform_info.original_url == url
        assert platform_info.extra_info is not None
        assert "detection_method" in platform_info.extra_info


class TestPlatformDetectorIntegration:
    """平台检测器集成测试"""
    
    def test_backward_compatibility(self):
        """测试向后兼容性"""
        from app.validators.video_url_validator import is_supported_video_url
        
        # 测试原有函数是否仍然工作
        assert is_supported_video_url("https://www.bilibili.com/video/BV1xx411c7mT") is True
        assert is_supported_video_url("https://youtu.be/dQw4w9WgXcQ") is True
        assert is_supported_video_url("https://vimeo.com/123") is False
    
    def test_performance(self):
        """测试性能：确保检测速度足够快"""
        import time
        
        test_urls = [
            "https://www.bilibili.com/video/BV1xx411c7mT",
            "https://youtu.be/dQw4w9WgXcQ",
            "b23.tv/test",
        ]
        
        # 多次测试平均时间
        total_time = 0
        iterations = 100
        
        for _ in range(iterations):
            start_time = time.time()
            for url in test_urls:
                detect_platform(url)
            end_time = time.time()
            total_time += (end_time - start_time)
        
        avg_time = total_time / iterations
        # 确保平均每次检测时间少于100ms（很宽松的要求）
        assert avg_time < 0.1


if __name__ == "__main__":
    # 运行基本测试
    detector = PlatformDetector()
    
    test_urls = [
        "https://www.bilibili.com/video/BV1xx411c7mT",
        "https://youtu.be/dQw4w9WgXcQ", 
        "b23.tv/test",
        "https://vimeo.com/123",  # 应该失败
    ]
    
    print("=== URL平台检测测试 ===")
    for url in test_urls:
        try:
            result = detector.detect_platform(url)
            print(f"✅ {url}")
            print(f"   平台: {result.platform}")
            print(f"   置信度: {result.confidence}")
            print(f"   检测方法: {result.extra_info['detection_method']}")
            print()
        except Exception as e:
            print(f"❌ {url}")
            print(f"   错误: {e}")
            print()
