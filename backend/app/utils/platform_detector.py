# app/utils/platform_detector.py
"""
URL平台自动检测模块
实现基于URL的智能平台识别功能
"""

import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import httpx
import asyncio
from dataclasses import dataclass

from app.exceptions.platform_exceptions import (
    PlatformDetectionError,
    UnsupportedPlatformError,
    InvalidVideoURLError,
    PlatformDetectionTimeoutError,
)


@dataclass
class PlatformInfo:
    """平台信息数据类"""
    platform: str
    confidence: float = 1.0
    original_url: str = ""
    normalized_url: str = ""
    extra_info: Optional[Dict[str, Any]] = None


class PlatformDetector:
    """平台检测器"""
    
    # 扩展的平台模式定义
    PLATFORM_PATTERNS = {
        "bilibili": {
            # BV号格式
            "main": r"(https?://)?(www\.)?bilibili\.com/video/[a-zA-Z0-9]+",
            # 短链接
            "short": r"(https?://)?(b23\.tv|Bili23\.tv)/[a-zA-Z0-9]+",
            # av号格式
            "av": r"(https?://)?(www\.)?bilibili\.com/video/av\d+",
            # 直播页面
            "live": r"(https?://)?(live\.)?bilibili\.com/\d+",
            # 番剧页面
            "bangumi": r"(https?://)?(www\.)?bilibili\.com/bangumi/play/(ss|ep)\d+",
        },
        "youtube": {
            # 标准视频链接
            "main": r"(https?://)?(www\.)?youtube\.com/watch\?v=[\w\-]+",
            # 短链接
            "short": r"(https?://)?(youtu\.be/)[\w\-]+",
            # Shorts视频
            "shorts": r"(https?://)?(www\.)?youtube\.com/shorts/[\w\-]+",
            # 播放列表
            "playlist": r"(https?://)?(www\.)?youtube\.com/playlist\?list=[\w\-]+",
            # 频道视频
            "channel": r"(https?://)?(www\.)?youtube\.com/(c/|user/|@)[\w\-]+/videos",
        }
    }
    
    # 平台域名映射
    DOMAIN_PLATFORM_MAP = {
        "bilibili.com": "bilibili",
        "b23.tv": "bilibili", 
        "bili23.tv": "bilibili",
        "live.bilibili.com": "bilibili",
        "youtube.com": "youtube",
        "youtu.be": "youtube",
        "www.youtube.com": "youtube",
    }
    
    def __init__(self, timeout: float = 5.0):
        """
        初始化平台检测器
        
        Args:
            timeout: HTTP请求超时时间（秒）
        """
        self.timeout = timeout
        self._compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, Dict[str, re.Pattern]]:
        """编译所有正则表达式模式"""
        compiled = {}
        for platform, patterns in self.PLATFORM_PATTERNS.items():
            compiled[platform] = {
                name: re.compile(pattern)
                for name, pattern in patterns.items()
            }
        return compiled
    
    def detect_platform(self, url: str, timeout: float = None) -> PlatformInfo:
        """
        检测URL所属平台
        
        Args:
            url: 待检测的视频URL
            timeout: 自定义超时时间（可选）
            
        Returns:
            PlatformInfo: 包含平台信息的对象
            
        Raises:
            InvalidVideoURLError: URL格式无效
            UnsupportedPlatformError: 不支持的平台
            PlatformDetectionError: 检测过程中的其他错误
        """
        try:
            # URL预处理
            normalized_url, is_valid = self._preprocess_url(url)
            if not is_valid:
                raise InvalidVideoURLError(url)
            
            # 快速域名检测
            platform_info = self._detect_by_domain(normalized_url)
            if platform_info:
                return platform_info
            
            # 正则表达式模式匹配
            platform_info = self._detect_by_pattern(normalized_url)
            if platform_info:
                return platform_info
            
            # HTTP请求检测（用于短链接解析）
            if timeout is None:
                timeout = self.timeout
            
            platform_info = self._detect_by_http(normalized_url, timeout)
            if platform_info:
                return platform_info
            
            # 如果所有方法都失败，抛出不支持平台异常
            raise UnsupportedPlatformError(url)
            
        except httpx.TimeoutException:
            raise PlatformDetectionTimeoutError(url)
        except Exception as e:
            if isinstance(e, (InvalidVideoURLError, UnsupportedPlatformError, PlatformDetectionError)):
                raise
            raise PlatformDetectionError(f"平台检测失败: {str(e)}", url)
    
    def _preprocess_url(self, url: str) -> tuple[str, bool]:
        """
        URL预处理
        
        Args:
            url: 原始URL
            
        Returns:
            tuple: (处理后的URL, 是否有效)
        """
        # 添加协议头如果缺失
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 基本格式验证
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return url, False
        except Exception:
            return url, False
        
        return url, True
    
    def _detect_by_domain(self, url: str) -> Optional[PlatformInfo]:
        """基于域名进行快速检测"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 精确域名匹配
            if domain in self.DOMAIN_PLATFORM_MAP:
                platform = self.DOMAIN_PLATFORM_MAP[domain]
                return PlatformInfo(
                    platform=platform,
                    confidence=1.0,
                    original_url=url,
                    normalized_url=url,
                    extra_info={"detection_method": "domain"}
                )
            
            # 部分域名匹配（处理www前缀等）
            for domain_key, platform in self.DOMAIN_PLATFORM_MAP.items():
                if domain_key in domain or domain in domain_key:
                    return PlatformInfo(
                        platform=platform,
                        confidence=0.9,
                        original_url=url,
                        normalized_url=url,
                        extra_info={"detection_method": "domain_partial"}
                    )
                    
        except Exception:
            pass
        
        return None
    
    def _detect_by_pattern(self, url: str) -> Optional[PlatformInfo]:
        """基于正则表达式模式进行检测"""
        for platform, patterns in self._compiled_patterns.items():
            for pattern_name, pattern in patterns.items():
                if pattern.match(url):
                    return PlatformInfo(
                        platform=platform,
                        confidence=0.95,
                        original_url=url,
                        normalized_url=url,
                        extra_info={
                            "detection_method": "pattern",
                            "pattern_name": pattern_name
                        }
                    )
        
        return None
    

    
    def _detect_by_http(self, url: str, timeout: float) -> Optional[PlatformInfo]:
        """同步HTTP检测包装器"""
        try:
            # 直接使用同步的httpx客户端，避免异步复杂性
            return self._detect_by_http_sync(url, timeout)
        except Exception:
            return None
    
    def _detect_by_http_sync(self, url: str, timeout: float) -> Optional[PlatformInfo]:
        """同步HTTP检测（用于短链接等）"""
        try:
            with httpx.Client(timeout=timeout) as client:
                # 仅对短链接域名进行HTTP检测
                parsed = urlparse(url)
                if parsed.netloc.lower() in ["b23.tv", "bili23.tv"]:
                    response = client.head(url, follow_redirects=True)
                    
                    # 检查重定向后的URL
                    if response.history:
                        final_url = response.url
                        platform_info = self._detect_by_domain(str(final_url))
                        if platform_info:
                            platform_info.normalized_url = str(final_url)
                            platform_info.extra_info["detection_method"] = "http_redirect"
                            platform_info.extra_info["original_domain"] = parsed.netloc
                            return platform_info
                            
        except Exception:
            pass
        
        return None
    
    def get_supported_platforms(self) -> list[str]:
        """获取所有支持的平台列表"""
        return list(self.PLATFORM_PATTERNS.keys())
    
    def is_supported_url(self, url: str) -> bool:
        """检查URL是否受支持（便捷方法）"""
        try:
            self.detect_platform(url)
            return True
        except (UnsupportedPlatformError, InvalidVideoURLError):
            return False


# 全局实例
platform_detector = PlatformDetector()


def detect_platform(url: str, timeout: float = None) -> PlatformInfo:
    """
    检测URL平台（便捷函数）
    
    Args:
        url: 待检测的视频URL
        timeout: 超时时间（可选）
        
    Returns:
        PlatformInfo: 平台信息对象
        
    Raises:
        InvalidVideoURLError: URL格式无效
        UnsupportedPlatformError: 不支持的平台
    """
    return platform_detector.detect_platform(url, timeout)


def is_supported_platform_url(url: str) -> bool:
    """
    检查URL是否受支持（便捷函数）
    
    Args:
        url: 待检查的视频URL
        
    Returns:
        bool: 是否受支持
    """
    return platform_detector.is_supported_url(url)


def get_supported_platforms() -> list[str]:
    """
    获取支持的平台列表（便捷函数）
    
    Returns:
        list[str]: 支持的平台名称列表
    """
    return platform_detector.get_supported_platforms()


# 向后兼容性：保留原有的验证函数
def is_supported_video_url(url: str) -> bool:
    """向后兼容：保留原有的验证函数"""
    return is_supported_platform_url(url)
