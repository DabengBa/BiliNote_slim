"""
验证API错误返回格式测试脚本
模拟前端期望的响应格式
"""
import json
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.note import router

# 创建测试应用
app = FastAPI()
app.include_router(router, prefix="/api/note")

client = TestClient(app)


def test_error_response_format():
    """测试错误响应格式符合前端期望"""

    # 尝试使用不支持的平台
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

    print("=" * 60)
    print("API 错误响应格式验证")
    print("=" * 60)
    print(f"HTTP状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

    # 验证响应格式符合前端期望
    assert response.status_code == 422, f"期望状态码422，实际{response.status_code}"

    response_data = response.json()

    # 前端期望的格式：IResponse interface
    # {
    #   code: number;
    #   msg: string;
    #   data: T;
    # }
    assert "code" in response_data, "响应中缺少'code'字段"
    assert "msg" in response_data, "响应中缺少'msg'字段"
    assert "data" in response_data, "响应中缺少'data'字段"

    # 验证字段值
    assert response_data["code"] == 300101, f"期望错误码300101，实际{response_data['code']}"
    assert response_data["msg"] == "选择的平台不受支持", f"期望错误信息，实际{response_data['msg']}"

    print("✅ 响应格式验证通过")
    print(f"   - HTTP状态码: {response.status_code} ✓")
    print(f"   - 错误码: {response_data['code']} ✓")
    print(f"   - 错误信息: {response_data['msg']} ✓")
    print(f"   - 数据字段: {response_data['data']} ✓")
    print()

    # 前端拦截器期望的行为
    print("前端拦截器处理逻辑:")
    print("-" * 60)
    if response_data["code"] == 0:
        print("✓ 业务成功，返回 data 部分")
    else:
        print(f"✓ 业务错误，显示错误消息: '{response_data['msg']}'")
        print("✓ 拒绝Promise，调用方可捕获并处理")
    print()

    print("=" * 60)
    print("✅ 所有验证通过！API错误格式完全符合前端期望")
    print("=" * 60)


if __name__ == "__main__":
    test_error_response_format()
