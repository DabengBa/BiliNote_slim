from pydantic import AnyUrl, validator, BaseModel, field_validator
import re
from urllib.parse import urlparse

SUPPORTED_PLATFORMS = {
    "bilibili": r"(https?://)?(www\.)?bilibili\.com/video/[a-zA-Z0-9]+",
    "youtube": r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+",
}


def is_supported_video_url(url: str) -> bool:
    # 如果没有协议头，添加http://以便urlparse正确解析
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed = urlparse(url)

    # 检查是否为Bilibili的短链接
    if parsed.netloc == "b23.tv":
        return True

    # 检查是否为YouTube短链接
    if parsed.netloc == "youtu.be":
        return True

    for name, pattern in SUPPORTED_PLATFORMS.items():
        if re.match(pattern, url):
            return True
    return False


class VideoRequest(BaseModel):
    url: AnyUrl
    platform: str

    @field_validator("url")
    def validate_video_url(cls, v):
        if not is_supported_video_url(str(v)):
            raise ValueError("暂不支持该视频平台或链接格式无效")
        return v
