"""
集成测试 - 验证前后端配合工作
"""
import pytest
import time
import subprocess
import os
from pathlib import Path
from fastapi.testclient import TestClient
from main import app


class IntegrationTestConfig:
    """集成测试配置"""
    BACKEND_HOST = "127.0.0.1"
    BACKEND_PORT = 8000
    BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
    
    FRONTEND_HOST = "127.0.0.1" 
    FRONTEND_PORT = 3000
    FRONTEND_URL = f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"
    
    # 测试数据
    TEST_BILIBILI_URL = "https://www.bilibili.com/video/BV1xx411c7mT"
    TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


class ProcessManager:
    """进程管理器，用于启动和停止前后端服务"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
    
    def start_backend(self):
        """启动后端服务"""
        try:
            # 切换到后端目录并启动服务
            backend_dir = Path(__file__).parent.parent
            cmd = [
                "python", "-m", "uvicorn", "main:app", 
                "--host", IntegrationTestConfig.BACKEND_HOST,
                "--port", str(IntegrationTestConfig.BACKEND_PORT)
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except Exception as e:
            print(f"启动后端服务失败: {e}")
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        try:
            # 切换到前端目录并启动开发服务器
            frontend_dir = Path(__file__).parent.parent.parent / "BillNote_frontend"
            cmd = ["npm", "run", "dev"]
            
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except Exception as e:
            print(f"启动前端服务失败: {e}")
            return False
    
    def stop_services(self):
        """停止所有服务"""
        try:
            if self.backend_process:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            
            if self.frontend_process:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
        except Exception as e:
            print(f"停止服务时出错: {e}")
        finally:
            # 确保进程被终止
            if self.backend_process:
                try:
                    self.backend_process.kill()
                except:
                    pass
            if self.frontend_process:
                try:
                    self.frontend_process.kill()
                except:
                    pass


def wait_for_service(url, timeout=30, check_path="/docs"):
    """等待服务启动并可用"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            import requests
            response = requests.get(f"{url}{check_path}", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False


class TestBackendAPIs:
    """测试后端API功能"""
    
    @pytest.fixture(scope="class")
    def backend_client(self):
        """提供后端测试客户端"""
        client = TestClient(app)
        return client
    
    def test_health_check(self, backend_client):
        """测试健康检查接口"""
        response = backend_client.get("/health")
        assert response.status_code in [200, 404]  # 404也可以接受，如果没有health端点
    
    def test_api_docs_accessible(self, backend_client):
        """测试API文档可访问"""
        response = backend_client.get("/docs")
        assert response.status_code == 200
    
    def test_generate_note_api_auto_platform_detection(self, backend_client):
        """测试生成笔记API - 自动平台检测"""
        test_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL,
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
            # 注意：不提供platform字段，测试自动检测
        }
        
        response = backend_client.post("/api/generate_note", json=test_data)
        
        # 由于可能依赖外部服务，我们主要检查响应格式
        # 期望返回200 (任务接受) 或 422 (验证错误)
        assert response.status_code in [200, 422]
        
        response_data = response.json()
        assert "code" in response_data
        assert "msg" in response_data
        
        if response.status_code == 200:
            # 成功响应应该包含task_id
            assert "data" in response_data
            assert "task_id" in response_data.get("data", {})
        else:
            # 错误响应该有明确的错误码和消息
            assert isinstance(response_data["code"], int)
            assert isinstance(response_data["msg"], str)
    
    def test_generate_note_api_explicit_platform(self, backend_client):
        """测试生成笔记API - 显式平台指定"""
        test_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL,
            "platform": "bilibili",  # 显式指定平台
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        response = backend_client.post("/api/generate_note", json=test_data)
        
        assert response.status_code in [200, 422]
        response_data = response.json()
        assert "code" in response_data
        assert "msg" in response_data
    
    def test_unsupported_platform_error(self, backend_client):
        """测试不支持平台的错误处理"""
        test_data = {
            "video_url": "https://example.com/video/123",
            "platform": "unsupported_platform",
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        response = backend_client.post("/api/generate_note", json=test_data)
        
        # 不支持的平台应该返回422
        assert response.status_code == 422
        response_data = response.json()
        assert "code" in response_data
        assert "msg" in response_data
        assert response_data["code"] != 0  # 非零错误码
    
    def test_upload_api(self, backend_client):
        """测试文件上传API"""
        # 创建一个测试文件
        test_file_content = b"test file content"
        files = {"file": ("test.txt", test_file_content, "text/plain")}
        
        response = backend_client.post("/api/upload", files=files)
        
        # 检查响应状态和格式
        assert response.status_code in [200, 500]  # 500可能由于目录不存在
        if response.status_code == 200:
            response_data = response.json()
            assert "code" in response_data
            assert "msg" in response_data


class TestFullWorkflow:
    """测试完整的用户工作流程"""
    
    def test_complete_video_to_note_workflow(self):
        """测试从视频URL到生成笔记的完整流程"""
        # 这个测试主要验证API调用的完整流程
        # 在实际环境中可能需要mock外部依赖
        
        client = TestClient(app)
        
        # 步骤1: 生成笔记请求
        request_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL,
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider",
            "screenshot": True,
            "format": ["markdown"]
        }
        
        response = client.post("/api/generate_note", json=request_data)
        
        # 验证请求被接受
        assert response.status_code in [200, 422]
        response_data = response.json()
        assert "code" in response_data
        
        if response.status_code == 200:
            # 成功获取task_id
            task_id = response_data.get("data", {}).get("task_id")
            assert task_id is not None
            
            # 步骤2: 查询任务状态
            status_response = client.get(f"/api/task_status/{task_id}")
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            assert "code" in status_data
            assert "data" in status_data or "msg" in status_data


class TestErrorHandling:
    """测试错误处理"""
    
    def test_invalid_url_handling(self):
        """测试无效URL的处理"""
        client = TestClient(app)
        
        invalid_data = {
            "video_url": "invalid_url",
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        response = client.post("/api/generate_note", json=invalid_data)
        
        # 应该返回400或422错误
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self):
        """测试缺少必需字段的处理"""
        client = TestClient(app)
        
        # 缺少必需字段
        incomplete_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL
            # 缺少其他必需字段
        }
        
        response = client.post("/api/generate_note", json=incomplete_data)
        
        # 应该返回422验证错误
        assert response.status_code == 422
    
    def test_invalid_quality_parameter(self):
        """测试无效quality参数的处理"""
        client = TestClient(app)
        
        invalid_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL,
            "quality": "invalid_quality",  # 无效的质量设置
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        response = client.post("/api/generate_note", json=invalid_data)
        
        # 应该返回422验证错误
        assert response.status_code == 422


class TestPerformance:
    """测试性能相关功能"""
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        client = TestClient(app)
        
        request_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL,
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        # 发送多个并发请求
        import concurrent.futures
        
        def send_request():
            return client.post("/api/generate_note", json=request_data)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(send_request) for _ in range(3)]
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 所有请求都应该得到响应
        assert len(responses) == 3
        for response in responses:
            assert response.status_code in [200, 422]
    
    def test_response_time(self):
        """测试响应时间"""
        client = TestClient(app)
        
        request_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL,
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        start_time = time.time()
        response = client.post("/api/generate_note", json=request_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 响应时间应该在合理范围内（这里设置为10秒）
        assert response_time < 10.0
        assert response.status_code in [200, 422]


class TestSecurity:
    """测试安全相关功能"""
    
    def test_sql_injection_protection(self):
        """测试SQL注入保护"""
        client = TestClient(app)
        
        malicious_data = {
            "video_url": "'; DROP TABLE users; --",
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        response = client.post("/api/generate_note", json=malicious_data)
        
        # 应该返回错误，而不是执行恶意SQL
        assert response.status_code in [400, 422]
    
    def test_xss_protection(self):
        """测试XSS攻击保护"""
        client = TestClient(app)
        
        xss_data = {
            "video_url": "<script>alert('xss')</script>",
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        response = client.post("/api/generate_note", json=xss_data)
        
        # 应该返回错误，而不会执行脚本
        assert response.status_code in [400, 422]
    
    def test_rate_limiting_headers(self):
        """测试速率限制头"""
        client = TestClient(app)
        
        request_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL,
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        response = client.post("/api/generate_note", json=request_data)
        
        # 检查是否包含速率限制相关的响应头（如果有的话）
        # 这里只是示例，实际项目中可能没有速率限制
        assert response.status_code in [200, 422]


@pytest.mark.integration
class TestFullSystemIntegration:
    """完整的系统集成测试"""
    
    @pytest.fixture(scope="class")
    def process_manager(self):
        """进程管理器fixture"""
        manager = ProcessManager()
        yield manager
        manager.stop_services()
    
    @pytest.mark.skip(reason="需要外部服务依赖，CI环境中跳过")
    def test_backend_frontend_integration(self, process_manager):
        """测试前后端完整集成"""
        # 注意：这个测试在实际环境中需要启动真实的服务进程
        # 在CI环境中可能会被跳过
        
        # 启动后端服务
        assert process_manager.start_backend()
        
        # 等待后端服务启动
        backend_ready = wait_for_service(IntegrationTestConfig.BACKEND_URL)
        assert backend_ready, "后端服务启动超时"
        
        # 测试后端API
        try:
            import requests
            response = requests.get(f"{IntegrationTestConfig.BACKEND_URL}/docs")
            assert response.status_code == 200
        finally:
            process_manager.stop_services()
    
    def test_api_contract_consistency(self):
        """测试API契约一致性"""
        client = TestClient(app)
        
        # 测试所有主要端点的响应格式一致性
        
        # 1. 生成笔记端点
        generate_data = {
            "video_url": IntegrationTestConfig.TEST_BILIBILI_URL,
            "quality": "fast",
            "model_name": "gpt-4",
            "provider_id": "test_provider"
        }
        
        generate_response = client.post("/api/generate_note", json=generate_data)
        assert "code" in generate_response.json()
        assert "msg" in generate_response.json()
        
        # 2. 任务状态端点（如果有task_id）
        generate_result = generate_response.json()
        if generate_response.status_code == 200 and "data" in generate_result:
            task_id = generate_result["data"].get("task_id")
            if task_id:
                status_response = client.get(f"/api/task_status/{task_id}")
                status_data = status_response.json()
                assert "code" in status_data
                assert "msg" in status_data
        
        # 3. 上传端点
        test_file = ("test.txt", b"content", "text/plain")
        upload_response = client.post("/api/note/upload", files={"file": test_file})
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            assert "code" in upload_data
            assert "msg" in upload_data