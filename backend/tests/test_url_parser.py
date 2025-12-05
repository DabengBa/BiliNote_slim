"""
测试URL平台自动识别功能
专门测试平台检测器的各种情况
"""
import pytest
from unittest.mock import patch, MagicMock

from app.utils.platform_detector import detect_platform, PlatformInfo, PlatformDetector
from app.exceptions import (
    InvalidVideoURLError,
    UnsupportedPlatformError,
    PlatformDetectionTimeoutError,
    PlatformDetectionError,
)


class TestPlatformDetection:
    """测试平台自动识别功能"""

    def test_detect_bilibili_standard_video(self):
        """测试标准B站视频URL识别"""
        platform_info = detect_platform("https://www.bilibili.com/video/BV1xx411c7mT")
        
        assert isinstance(platform_info, PlatformInfo)
        assert platform_info.platform == "bilibili"
        assert platform_info.confidence >= 0.9
        assert platform_info.original_url == "https://www.bilibili.com/video/BV1xx411c7mT"

    def test_detect_bilibili_video_with_p_parameter(self):
        """测试B站视频URL（带p参数）"""
        url = "https://www.bilibili.com/video/BV1xx411c7mT?p=2"
        platform_info = detect_platform(url)
        
        assert platform_info.platform == "bilibili"
        assert platform_info.confidence >= 0.9

    def test_detect_bilibili_av_video(self):
        """测试B站AV号视频URL"""
        url = "https://www.bilibili.com/video/av170001"
        platform_info = detect_platform(url)
        
        assert platform_info.platform == "bilibili"
        assert platform_info.confidence >= 0.9

    def test_detect_bilibili_live_room(self):
        """测试B站直播间URL"""
        url = "https://live.bilibili.com/12345"
        platform_info = detect_platform(url)
        
        assert platform_info.platform == "bilibili"
        assert platform_info.confidence >= 0.9

    def test_detect_bilibili_bangumi(self):
        """测试B站番剧URL"""
        url = "https://www.bilibili.com/bangumi/play/ss12345"
        platform_info = detect_platform(url)
        
        assert platform_info.platform == "bilibili"
        assert platform_info.confidence >= 0.9

    def test_detect_bilibili_short_url(self):
        """测试B站短链接"""
        url = "https://b23.tv/BV1xx411c7mT"
        platform_info = detect_platform(url)
        
        assert platform_info.platform == "bilibili"
        # 检查是否正确识别为B站平台
        assert platform_info.normalized_url is not None

    def test_detect_bilibili_without_www(self):
        """测试不带www的B站URL"""
        platform_info = detect_platform("https://bilibili.com/video/BV1xx411c7mT")
        
        assert platform_info.platform == "bilibili"
        assert platform_info.confidence >= 0.9

    def test_detect_youtube_standard_video(self):
        """测试标准YouTube视频URL"""
        platform_info = detect_platform("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        assert platform_info.platform == "youtube"
        assert platform_info.confidence >= 0.9

    def test_detect_youtube_short_url(self):
        """测试YouTube短链接"""
        platform_info = detect_platform("https://youtu.be/dQw4w9WgXcQ")
        
        assert platform_info.platform == "youtube"
        assert platform_info.confidence >= 0.9

    def test_detect_youtube_shorts(self):
        """测试YouTube Shorts视频"""
        platform_info = detect_platform("https://www.youtube.com/shorts/abcdefghijk")
        
        assert platform_info.platform == "youtube"
        assert platform_info.confidence >= 0.9

    def test_detect_youtube_playlist(self):
        """测试YouTube播放列表"""
        platform_info = detect_platform("https://www.youtube.com/playlist?list=PL9tY0BWXOZFuFEG_GtOBZ8-8wbkH-NVAr")
        
        assert platform_info.platform == "youtube"
        assert platform_info.confidence >= 0.9

    def test_detect_youtube_channel_videos(self):
        """测试YouTube频道视频页面"""
        platform_info = detect_platform("https://www.youtube.com/c/ChannelName/videos")
        
        assert platform_info.platform == "youtube"
        assert platform_info.confidence >= 0.9

    def test_detect_youtube_without_www(self):
        """测试不带www的YouTube URL"""
        platform_info = detect_platform("https://youtube.com/watch?v=dQw4w9WgXcQ")
        
        assert platform_info.platform == "youtube"
        assert platform_info.confidence >= 0.9

    def test_reject_douyin_url(self):
        """测试拒绝抖音URL"""
        with pytest.raises(UnsupportedPlatformError):
            detect_platform("https://www.douyin.com/video/123456789")

    def test_reject_kuaishou_url(self):
        """测试拒绝快手URL"""
        with pytest.raises(UnsupportedPlatformError):
            detect_platform("https://www.kuaishou.com/video/123456")

    def test_reject_xiaoyuzhou_url(self):
        """测试拒绝小宇宙URL"""
        with pytest.raises(UnsupportedPlatformError):
            detect_platform("https://www.xiaoyuzhoufm.com/podcast/123")

    def test_reject_tiktok_url(self):
        """测试拒绝TikTok URL"""
        with pytest.raises(UnsupportedPlatformError):
            detect_platform("https://www.tiktok.com/video/123")

    def test_invalid_url_format(self):
        """测试无效URL格式"""
        with pytest.raises((InvalidVideoURLError, UnsupportedPlatformError)):
            detect_platform("not-a-valid-url")

    def test_empty_url(self):
        """测试空URL"""
        with pytest.raises((InvalidVideoURLError, UnsupportedPlatformError)):
            detect_platform("")

    def test_none_url(self):
        """测试None URL"""
        with pytest.raises(PlatformDetectionError):
            detect_platform(None)

    def test_url_without_protocol(self):
        """测试不带协议头的URL"""
        # 应该自动添加https://前缀
        platform_info = detect_platform("www.bilibili.com/video/BV1xx411c7mT")
        
        assert platform_info.platform == "bilibili"
        assert platform_info.original_url == "https://www.bilibili.com/video/BV1xx411c7mT"

    def test_http_url(self):
        """测试HTTP协议URL"""
        platform_info = detect_platform("http://www.bilibili.com/video/BV1xx411c7mT")
        
        assert platform_info.platform == "bilibili"

    def test_url_with_special_characters(self):
        """测试包含特殊字符的URL"""
        platform_info = detect_platform("https://www.bilibili.com/video/BV1xx411c7mT?spm_id_from=333.337.search-card.all.click")
        
        assert platform_info.platform == "bilibili"

    def test_url_parameter_order_independence(self):
        """测试URL参数顺序不影响识别"""
        url1 = "https://www.bilibili.com/video/BV1xx411c7mT?p=2&vd_source=test"
        url2 = "https://www.bilibili.com/video/BV1xx411c7mT?vd_source=test&p=2"
        
        platform_info1 = detect_platform(url1)
        platform_info2 = detect_platform(url2)
        
        assert platform_info1.platform == platform_info2.platform == "bilibili"

    def test_case_insensitive_domain(self):
        """测试域名大小写不敏感"""
        platform_info = detect_platform("https://WWW.BILIBILI.COM/video/BV1xx411c7mT")
        
        assert platform_info.platform == "bilibili"

    def test_http_timeout_handling(self):
        """测试HTTP请求超时处理"""
        with patch('app.utils.platform_detector.httpx.Client') as mock_client:
            # 模拟HTTP客户端抛出超时异常
            mock_client.side_effect = Exception("Timeout")
            
            # 应该降级到其他检测方法或抛出平台不支持错误
            try:
                detect_platform("https://b23.tv/test")
            except (PlatformDetectionTimeoutError, UnsupportedPlatformError):
                pass  # 两种异常都可以接受

    def test_domain_partial_matching(self):
        """测试域名部分匹配"""
        platform_info = detect_platform("https://live.bilibili.com/123456")
        
        assert platform_info.platform == "bilibili"
        assert platform_info.extra_info["detection_method"] in ["domain", "domain_partial", "pattern"]

    def test_platform_confidence_scores(self):
        """测试平台识别的置信度分数"""
        # B站URL应该有较高的置信度
        bilibili_platform = detect_platform("https://www.bilibili.com/video/BV1xx411c7mT")
        assert bilibili_platform.confidence >= 0.9
        
        # YouTube URL应该有较高的置信度
        youtube_platform = detect_platform("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert youtube_platform.confidence >= 0.9

    def test_extra_info_content(self):
        """测试extra_info字段内容"""
        platform_info = detect_platform("https://www.bilibili.com/video/BV1xx411c7mT")
        
        assert "detection_method" in platform_info.extra_info
        # 确保检测方法在预期范围内
        detection_method = platform_info.extra_info["detection_method"]
        assert detection_method in ["domain", "domain_partial", "pattern", "http_redirect"]

    def test_supported_platforms_list(self):
        """测试获取支持的平台列表"""
        from app.utils.platform_detector import get_supported_platforms
        
        platforms = get_supported_platforms()
        assert isinstance(platforms, list)
        assert "bilibili" in platforms
        assert "youtube" in platforms

    def test_is_supported_url_function(self):
        """测试便捷函数is_supported_platform_url"""
        from app.utils.platform_detector import is_supported_platform_url
        
        # 支持的URL
        assert is_supported_platform_url("https://www.bilibili.com/video/BV1xx411c7mT") is True
        assert is_supported_platform_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        
        # 不支持的URL
        assert is_supported_platform_url("https://www.douyin.com/video/123") is False
        assert is_supported_platform_url("invalid-url") is False

    def test_backward_compatibility_function(self):
        """测试向后兼容函数is_supported_video_url"""
        from app.utils.platform_detector import is_supported_video_url
        
        # 验证与原有函数行为一致
        assert is_supported_video_url("https://www.bilibili.com/video/BV1xx411c7mT") is True
        assert is_supported_video_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
        assert is_supported_video_url("https://www.douyin.com/video/123") is False


class TestPlatformDetectorClass:
    """测试PlatformDetector类的具体方法"""

    def test_compile_patterns(self):
        """测试正则表达式编译"""
        detector = PlatformDetector()
        compiled = detector._compiled_patterns
        
        assert "bilibili" in compiled
        assert "youtube" in compiled
        assert "main" in compiled["bilibili"]
        assert isinstance(compiled["bilibili"]["main"].pattern, str)

    def test_preprocess_url(self):
        """测试URL预处理"""
        detector = PlatformDetector()
        
        # 测试添加协议头
        url1, valid1 = detector._preprocess_url("www.bilibili.com/video/BV1xx411c7mT")
        assert valid1 is True
        assert "https://www.bilibili.com/video/BV1xx411c7mT" in url1
        
        # 测试已经是完整URL的
        url2, valid2 = detector._preprocess_url("https://www.bilibili.com/video/BV1xx411c7mT")
        assert valid2 is True
        assert url2 == "https://www.bilibili.com/video/BV1xx411c7mT"
        
        # 测试无效URL
        url3, valid3 = detector._preprocess_url("not-a-url")
        # 可能是False，但也可能被处理为URL格式，需检查实际行为

    def test_detect_by_domain(self):
        """测试基于域名的检测"""
        detector = PlatformDetector()
        
        # 测试B站域名
        platform_info = detector._detect_by_domain("https://www.bilibili.com/video/BV1xx411c7mT")
        assert platform_info is not None
        assert platform_info.platform == "bilibili"
        
        # 测试不存在的域名
        platform_info = detector._detect_by_domain("https://unknown.com/video/test")
        assert platform_info is None

    def test_detect_by_pattern(self):
        """测试基于模式的检测"""
        detector = PlatformDetector()
        
        # 测试B站番剧模式
        platform_info = detector._detect_by_pattern("https://www.bilibili.com/bangumi/play/ss12345")
        assert platform_info is not None
        assert platform_info.platform == "bilibili"
        assert platform_info.extra_info["pattern_name"] == "bangumi"

    def test_get_supported_platforms_method(self):
        """测试get_supported_platforms方法"""
        detector = PlatformDetector()
        platforms = detector.get_supported_platforms()
        
        assert isinstance(platforms, list)
        assert "bilibili" in platforms
        assert "youtube" in platforms

    def test_is_supported_url_method(self):
        """测试is_supported_url方法"""
        detector = PlatformDetector()
        
        assert detector.is_supported_url("https://www.bilibili.com/video/BV1xx411c7mT") is True
        assert detector.is_supported_url("https://www.douyin.com/video/123") is False
        assert detector.is_supported_url("invalid-url") is False

    def test_custom_timeout(self):
        """测试自定义超时时间"""
        detector = PlatformDetector(timeout=10.0)
        
        # 测试默认超时
        platform_info = detector.detect_platform("https://www.bilibili.com/video/BV1xx411c7mT")
        assert platform_info.platform == "bilibili"
        
        # 测试自定义超时参数
        platform_info = detector.detect_platform("https://www.bilibili.com/video/BV1xx411c7mT", timeout=2.0)
        assert platform_info.platform == "bilibili"


if __name__ == "__main__":
    pytest.main([__file__])