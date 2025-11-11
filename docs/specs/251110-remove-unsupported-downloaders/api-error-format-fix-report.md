# API错误返回格式修复报告

> **问题发现时间**: 2025-11-11 15:03
> **修复完成时间**: 2025-11-11 15:08
> **影响范围**: `/api/note/generate_note` 路由

## 问题描述

**原始问题**: 后端在捕获`NoteError`后抛出`HTTPException`，FastAPI将其包装为`{"detail": {"code": ..., "message": ...}}`格式，与前端期望的`{"code": ..., "msg": ...}`格式不匹配。

**影响**:
- 前端拦截器无法正确解析错误信息
- 用户看到"服务器错误"而非具体的"暂不支持该视频平台..."提示
- 不满足T015/T021的体验与监控需求

## 根本原因

1. **使用HTTPException**: `raise HTTPException(status_code=422, detail={...})`导致FastAPI自动包装响应
2. **后台任务异步处理**: `NoteError`在`background_tasks`中抛出，无法在路由层捕获
3. **响应格式不统一**: 未使用`ResponseWrapper`统一处理错误响应

## 解决方案

### 1. 扩展ResponseWrapper支持HTTP状态码
```python
@staticmethod
def error(msg="error", code=500, data=None, status_code: int = 500):
    """返回错误响应，可指定HTTP状态码"""
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "msg": str(msg),
            "data": data
        }
    )
```

### 2. 预检查平台支持
在提交后台任务前验证平台：
```python
# 预检查平台是否支持 - 在提交后台任务前验证
# 这样可以立即返回422错误，而不是等到后台任务失败
generator = NoteGenerator()
generator._get_downloader(data.platform)
```

### 3. 使用统一错误返回格式
```python
except NoteError as e:
    # 捕获业务错误，返回结构化错误码
    # 使用R.error确保返回格式与前端期望一致: {"code": ..., "msg": ...}
    return R.error(
        msg=e.message,
        code=e.code,
        status_code=422
    )
```

## 修改文件

1. **backend/app/utils/response.py**
   - 扩展`error()`方法支持`status_code`参数

2. **backend/app/routers/note.py**
   - 添加平台预检查
   - 使用`R.error()`返回统一错误格式
   - 移除HTTPException的使用

3. **backend/tests/test_note_router.py**
   - 更新所有测试用例验证新响应格式
   - 验证HTTP状态码为422
   - 验证响应结构为`{"code": ..., "msg": ...}`

## 测试验证

**所有测试通过** (17/17):
- 路由测试: 5/5 ✓
  - `test_generate_rejects_douyin_platform` ✓
  - `test_generate_rejects_kuaishou_platform` ✓
  - `test_generate_rejects_tiktok_platform` ✓
  - `test_error_code_consistency` ✓
  - `test_generate_accepts_supported_platforms` ✓
- 服务层测试: 5/5 ✓
- URL验证器测试: 7/7 ✓

## 响应格式对比

### 修复前
```json
{
  "status_code": 422,
  "content": {
    "detail": {
      "code": 300101,
      "message": "选择的平台不受支持"
    }
  }
}
```

### 修复后
```json
{
  "status_code": 422,
  "content": {
    "code": 300101,
    "msg": "选择的平台不受支持",
    "data": null
  }
}
```

## 验收标准

| 标准 | 状态 | 验证结果 |
|------|------|----------|
| 返回HTTP 422状态码 | ✅ | 测试断言`assert response.status_code == 422`通过 |
| 响应格式为`{"code": ..., "msg": ...}` | ✅ | 测试断言响应包含正确字段 |
| 前端可正确解析错误信息 | ✅ | 格式与前端拦截器期望一致 |
| 所有不支持平台统一处理 | ✅ | 测试覆盖douyin/kuaishou/tiktok |

## 架构改进

1. **统一错误处理**: 使用`ResponseWrapper`而非直接抛出HTTPException
2. **预验证模式**: 在后台任务前进行预检查，避免异步错误处理复杂性
3. **类型安全**: 明确错误码和消息类型，减少格式错误

## 结论

✅ **问题已完全解决**
- API现在返回正确格式的错误响应
- 前端可以正确解析并显示用户友好的错误信息
- 所有验收标准均满足
- 17个测试用例全部通过
