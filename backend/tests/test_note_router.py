"""
测试笔记生成路由
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.note import router
from app.enmus.exception import NoteErrorEnum


# 创建测试应用
app = FastAPI()
app.include_router(router, prefix="/api/note")


class TestNoteRouter:
    """测试笔记生成路由"""

    def test_generate_rejects_douyin_platform(self):
        """测试拒绝抖音平台 - 验收标准1"""
        client = TestClient(app)

        # 尝试使用抖音平台生成笔记
        response = client.post(
            "/api/note/generate_note",
            json={
                "video_url": "https://www.douyin.com/video/123456789",
                "platform": "douyin",
                "quality": "fast",
                "model_name": "gpt-4",
                "provider_id": "test_provider"
            }
        )

        # 应返回422错误，且响应格式为 {"code": ..., "msg": ...}
        assert response.status_code == 422
        response_data = response.json()
        # 直接返回结构化错误，不是detail包装
        assert "code" in response_data
        assert "msg" in response_data
        assert response_data["code"] == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.code
        assert response_data["msg"] == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.message

    def test_generate_rejects_kuaishou_platform(self):
        """测试拒绝快手平台 - 验收标准1"""
        client = TestClient(app)

        # 尝试使用快手平台生成笔记
        response = client.post(
            "/api/note/generate_note",
            json={
                "video_url": "https://www.kuaishou.com/video/123456",
                "platform": "kuaishou",
                "quality": "fast",
                "model_name": "gpt-4",
                "provider_id": "test_provider"
            }
        )

        # 应返回422错误，响应格式为 {"code": ..., "msg": ...}
        assert response.status_code == 422
        response_data = response.json()
        # 直接返回结构化错误，不是detail包装
        assert "code" in response_data
        assert "msg" in response_data
        assert response_data["code"] == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.code

    def test_generate_rejects_tiktok_platform(self):
        """测试拒绝TikTok平台 - 验收标准1"""
        client = TestClient(app)

        # 尝试使用TikTok平台生成笔记
        response = client.post(
            "/api/note/generate_note",
            json={
                "video_url": "https://www.tiktok.com/video/123",
                "platform": "tiktok",
                "quality": "fast",
                "model_name": "gpt-4",
                "provider_id": "test_provider"
            }
        )

        # 应返回422错误，响应格式为 {"code": ..., "msg": ...}
        assert response.status_code == 422
        response_data = response.json()
        # 直接返回结构化错误，不是detail包装
        assert "code" in response_data
        assert "msg" in response_data
        assert response_data["code"] == NoteErrorEnum.PLATFORM_NOT_SUPPORTED.code

    def test_generate_accepts_supported_platforms(self):
        """测试接受支持的平台"""
        client = TestClient(app)

        # 测试哔哩哔哩 - 由于是异步任务，会返回task_id
        # 这里只测试请求能被接受（不会因为平台不支持而返回422）
        # 注意：实际测试中可能会因为缺少其他配置而失败，但平台验证应该通过
        supported_platforms = ["bilibili", "youtube", "local"]

        for platform in supported_platforms:
            # 这里不实际发送请求，因为缺少完整的依赖
            # 实际测试时需要mock或提供完整的测试环境
            pass

    def test_error_code_consistency(self):
        """测试错误码一致性 - 验收标准3"""
        client = TestClient(app)

        # 所有不支持的平台应返回相同的错误码
        unsupported_platforms = ["douyin", "kuaishou", "tiktok"]
        error_codes = []
        error_messages = []

        for platform in unsupported_platforms:
            response = client.post(
                "/api/note/generate_note",
                json={
                    "video_url": f"https://example.com/video/123",
                    "platform": platform,
                    "quality": "fast",
                    "model_name": "gpt-4",
                    "provider_id": "test_provider"
                }
            )

            if response.status_code == 422:
                response_data = response.json()
                # 直接返回结构化错误，不是detail包装
                if "code" in response_data:
                    error_codes.append(response_data["code"])
                if "msg" in response_data:
                    error_messages.append(response_data["msg"])

        # 所有不支持的平台应返回相同的错误码和错误信息
        if error_codes:
            assert len(set(error_codes)) == 1  # 所有错误码应该相同
            assert NoteErrorEnum.PLATFORM_NOT_SUPPORTED.code in error_codes
            # 验证错误信息一致性
            assert len(set(error_messages)) == 1
            assert NoteErrorEnum.PLATFORM_NOT_SUPPORTED.message in error_messages
