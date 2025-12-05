import re
from typing import Optional, Union
import requests
from urllib.parse import urlparse

from app.exceptions.platform_exceptions import (
    PlatformDetectionError,
    UnsupportedPlatformError,
    InvalidVideoURLError,
)
from app.utils.platform_detector import PlatformInfo


class VideoIDExtractionError(PlatformDetectionError):
    """视频ID提取异常"""
    
    def __init__(self, url: str, platform: str, message: str = None):
        self.platform = platform
        if not message:
            message = f"无法从 {platform} 平台URL中提取视频ID: {url}"
        super().__init__(message, url, "VIDEO_ID_EXTRACTION_FAILED")


def extract_video_id(url: Union[str, PlatformInfo], platform: str = None) -> Optional[str]:
    """
    从视频链接中提取视频 ID

    Args:
        url: 视频链接或PlatformInfo对象
        platform: 平台名（向后兼容，可选）
        
    Returns:
        提取到的视频 ID 或 None
        
    Raises:
        VideoIDExtractionError: 视频ID提取失败
        UnsupportedPlatformError: 不支持的平台
    """
    # 处理新的PlatformInfo接口
    if isinstance(url, PlatformInfo):
        platform = url.platform
        video_url = url.normalized_url or url.original_url
    else:
        video_url = url
        if not platform:
            raise InvalidVideoURLError(url)
    
    # 验证URL格式
    try:
        parsed = urlparse(video_url)
        if not parsed.scheme or not parsed.netloc:
            raise InvalidVideoURLError(video_url)
    except Exception as e:
        raise InvalidVideoURLError(video_url)
    
    try:
        if platform == "bilibili":
            return _extract_bilibili_id(video_url)
        elif platform == "youtube":
            return _extract_youtube_id(video_url)
        else:
            raise UnsupportedPlatformError(f"视频ID提取不支持平台: {platform}")
            
    except Exception as e:
        if isinstance(e, (PlatformDetectionError, UnsupportedPlatformError)):
            raise
        raise VideoIDExtractionError(video_url, platform, str(e))


def _extract_bilibili_id(url: str) -> str:
    """提取Bilibili视频ID"""
    # 如果是短链接，尝试解析真实链接
    if "b23.tv" in url or "bili23.tv" in url:
        resolved_url = resolve_bilibili_short_url(url)
        if resolved_url:
            url = resolved_url
    
    # 匹配BV号（如 BV1vc411b7Wa）
    bv_match = re.search(r"BV([0-9A-Za-z]+)", url)
    if bv_match:
        return f"BV{bv_match.group(1)}"
    
    # 匹配av号（如 av170001）
    av_match = re.search(r"av(\d+)", url)
    if av_match:
        return f"av{av_match.group(1)}"
    
    # 尝试从URL路径提取视频ID
    path_match = re.search(r"/video/([a-zA-Z0-9]+)", url)
    if path_match:
        return path_match.group(1)
    
    raise VideoIDExtractionError(url, "bilibili", "无法识别Bilibili视频ID格式")


def _extract_youtube_id(url: str) -> str:
    """提取YouTube视频ID"""
    # 匹配 v=xxxxx
    v_match = re.search(r"[?&]v=([0-9A-Za-z_-]{11})", url)
    if v_match:
        return v_match.group(1)
    
    # 匹配 youtu.be/xxxxx
    youtu_match = re.search(r"youtu\.be/([0-9A-Za-z_-]{11})", url)
    if youtu_match:
        return youtu_match.group(1)
    
    # 匹配 /shorts/xxxxx
    shorts_match = re.search(r"/shorts/([0-9A-Za-z_-]{11})", url)
    if shorts_match:
        return shorts_match.group(1)
    
    # 匹配 /embed/xxxxx
    embed_match = re.search(r"/embed/([0-9A-Za-z_-]{11})", url)
    if embed_match:
        return embed_match.group(1)
    
    raise VideoIDExtractionError(url, "youtube", "无法识别YouTube视频ID格式")


def resolve_bilibili_short_url(short_url: str) -> Optional[str]:
    """
    解析哔哩哔哩短链接以获取真实视频链接

    :param short_url: Bilibili短链接（如"https://b23.tv/xxxxxx"）
    :return: 真实的视频链接或None
    """
    try:
        response = requests.head(short_url, allow_redirects=True)
        return response.url
    except requests.RequestException as e:
        print(f"Error resolving short URL: {e}")
        return None
