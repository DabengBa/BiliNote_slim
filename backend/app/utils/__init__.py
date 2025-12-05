# app/utils/__init__.py
# URL平台检测相关工具
from .platform_detector import (
    PlatformDetector,
    PlatformInfo,
    detect_platform,
    is_supported_platform_url,
    get_supported_platforms,
    is_supported_video_url,  # 向后兼容
)
