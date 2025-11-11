"""
测试笔记服务
"""
import pytest
from app.services.note import NoteGenerator
from app.enmus.exception import NoteErrorEnum
from app.exceptions.note import NoteError


class TestNoteService:
    """测试笔记服务"""

    def test_reject_unsupported_platform_douyin(self):
        """测试拒绝抖音平台 - 验收标准1"""
        generator = NoteGenerator()

        # 尝试为抖音平台生成笔记应抛出NoteError
        with pytest.raises(NoteError) as exc_info:
            generator._get_downloader("douyin")

        assert exc_info.value.code == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.code
        assert exc_info.value.message == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.message

    def test_reject_unsupported_platform_kuaishou(self):
        """测试拒绝快手平台 - 验收标准1"""
        generator = NoteGenerator()

        # 尝试为快手平台生成笔记应抛出NoteError
        with pytest.raises(NoteError) as exc_info:
            generator._get_downloader("kuaishou")

        assert exc_info.value.code == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.code
        assert exc_info.value.message == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.message

    def test_reject_unsupported_platform_tiktok(self):
        """测试拒绝TikTok平台 - 验收标准1"""
        generator = NoteGenerator()

        # 尝试为TikTok平台生成笔记应抛出NoteError
        with pytest.raises(NoteError) as exc_info:
            generator._get_downloader("tiktok")

        assert exc_info.value.code == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.code
        assert exc_info.value.message == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.message

    def test_accept_supported_platforms(self):
        """测试接受支持的平台 - 验收标准4"""
        generator = NoteGenerator()

        # 支持的平台应该能正常获取下载器
        supported_platforms = ["bilibili", "youtube", "local"]

        for platform in supported_platforms:
            downloader = generator._get_downloader(platform)
            assert downloader is not None

    def test_all_unsupported_platforms_rejected(self):
        """测试所有不支持的平台都被拒绝 - 验收标准5"""
        generator = NoteGenerator()

        # 所有不支持的平台
        unsupported_platforms = [
            "douyin",
            "kuaishou",
            "tiktok",
            "xiaoyuzhou",
            "invalid_platform"
        ]

        for platform in unsupported_platforms:
            with pytest.raises(NoteError) as exc_info:
                generator._get_downloader(platform)

            assert exc_info.value.code == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.code
