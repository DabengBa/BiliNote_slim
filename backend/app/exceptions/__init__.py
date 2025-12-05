# app/exceptions/__init__.py
# 平台检测相关异常
from .platform_exceptions import (
    PlatformDetectionError,
    UnsupportedPlatformError,
    InvalidVideoURLError,
    PlatformDetectionTimeoutError,
    PlatformErrorEnum,
)