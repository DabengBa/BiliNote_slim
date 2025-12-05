# app/exceptions/platform_exceptions.py
"""
平台检测相关的异常类型定义
"""

import enum
from app.exceptions.biz_exception import BizException


class PlatformDetectionError(BizException):
    """平台检测异常基类"""
    
    def __init__(self, message: str, url: str = None, code: str = None):
        self.url = url
        super().__init__(message, code or "PLATFORM_DETECTION_ERROR")


class UnsupportedPlatformError(PlatformDetectionError):
    """不支持的平台异常"""
    
    def __init__(self, url: str):
        message = f"不支持的视频平台: {url}"
        super().__init__(message, url, "UNSUPPORTED_PLATFORM")


class InvalidVideoURLError(PlatformDetectionError):
    """无效视频URL异常"""
    
    def __init__(self, url: str):
        message = f"无效的视频URL格式: {url}"
        super().__init__(message, url, "INVALID_VIDEO_URL")


class PlatformDetectionTimeoutError(PlatformDetectionError):
    """平台检测超时异常"""
    
    def __init__(self, url: str):
        message = f"平台检测超时: {url}"
        super().__init__(message, url, "PLATFORM_DETECTION_TIMEOUT")


# 平台检测错误枚举
class PlatformErrorEnum(enum.Enum):
    """平台检测相关错误枚举"""
    
    UNSUPPORTED_PLATFORM = (300201, "不支持的视频平台")
    INVALID_VIDEO_URL = (300202, "无效的视频URL格式")
    PLATFORM_DETECTION_TIMEOUT = (300203, "平台检测超时")
    PLATFORM_DETECTION_ERROR = (300204, "平台检测错误")
    
    def __init__(self, code, message):
        self.code = code
        self.message = message
