# Requirements Document

## Introduction

本规范定义了 BiliNote 项目的系统性功能测试、性能检测和调试需求。BiliNote 是一个 AI 视频笔记生成工具，支持从 Bilibili、YouTube、抖音等平台提取视频内容并生成结构化 Markdown 笔记。本测试规范旨在确保各模块功能正常、性能达标，并提供有效的调试手段。

## Glossary

- **BiliNote**: AI 视频笔记生成系统
- **Provider**: AI 模型提供商（如 OpenAI、DeepSeek、Qwen）
- **Transcriber**: 音频转文字服务（如 Fast-Whisper、Groq）
- **Downloader**: 视频下载器，支持多平台
- **Note Generator**: 笔记生成核心服务
- **Task**: 异步笔记生成任务

## Requirements

### Requirement 1: 后端 API 可用性测试

**User Story:** As a 开发者, I want to 验证所有后端 API 端点的可用性, so that 确保服务正常运行。

#### Acceptance Criteria

1. WHEN 系统启动时 THEN BiliNote 后端 SHALL 在配置的端口上成功监听并响应健康检查请求
2. WHEN 调用 `/api/sys_health` 端点时 THEN BiliNote 后端 SHALL 返回 FFmpeg 安装状态
3. WHEN 调用 `/api/get_all_providers` 端点时 THEN BiliNote 后端 SHALL 返回所有已配置的 AI 提供商列表
4. WHEN 调用 `/api/model_list` 端点时 THEN BiliNote 后端 SHALL 返回所有可用模型列表
5. WHEN 调用不存在的端点时 THEN BiliNote 后端 SHALL 返回 404 状态码

### Requirement 2: 视频下载功能测试

**User Story:** As a 用户, I want to 验证视频下载功能在各平台的可用性, so that 确保能正确获取视频内容。

#### Acceptance Criteria

1. WHEN 提供有效的 Bilibili 视频 URL 时 THEN Downloader 模块 SHALL 成功提取视频 ID 并下载音频
2. WHEN 提供有效的 YouTube 视频 URL 时 THEN Downloader 模块 SHALL 成功提取视频 ID 并下载音频
3. WHEN 提供有效的抖音视频 URL 时 THEN Downloader 模块 SHALL 成功提取视频 ID 并下载音频
4. WHEN 提供无效或不支持的视频 URL 时 THEN Downloader 模块 SHALL 返回明确的错误信息
5. WHEN 下载过程中网络中断时 THEN Downloader 模块 SHALL 记录错误日志并更新任务状态为失败

### Requirement 3: 音频转写功能测试

**User Story:** As a 用户, I want to 验证音频转文字功能的准确性, so that 确保转写结果可用于笔记生成。

#### Acceptance Criteria

1. WHEN 提供有效的音频文件时 THEN Transcriber 模块 SHALL 返回文本转写结果
2. WHEN 使用 Fast-Whisper 转写器时 THEN Transcriber 模块 SHALL 在合理时间内完成转写
3. WHEN 音频文件格式不支持时 THEN Transcriber 模块 SHALL 返回格式错误信息
4. WHEN 音频文件为空或损坏时 THEN Transcriber 模块 SHALL 返回明确的错误信息

### Requirement 4: AI 笔记生成功能测试

**User Story:** As a 用户, I want to 验证 AI 笔记生成功能的完整性, so that 确保生成的笔记质量达标。

#### Acceptance Criteria

1. WHEN 提供有效的转写文本和模型配置时 THEN Note Generator SHALL 生成 Markdown 格式的笔记
2. WHEN 选择不同的笔记风格时 THEN Note Generator SHALL 根据风格参数调整输出格式
3. WHEN 启用截图功能时 THEN Note Generator SHALL 在笔记中包含视频截图
4. WHEN 启用链接功能时 THEN Note Generator SHALL 在笔记中包含原视频跳转链接
5. WHEN AI 提供商连接失败时 THEN Note Generator SHALL 返回连接错误信息并更新任务状态

### Requirement 5: Provider 管理功能测试

**User Story:** As a 管理员, I want to 验证 AI 提供商管理功能, so that 确保能正确配置和管理模型提供商。

#### Acceptance Criteria

1. WHEN 添加新的 Provider 时 THEN Provider Service SHALL 验证必填字段并保存到数据库
2. WHEN 更新 Provider 配置时 THEN Provider Service SHALL 更新对应记录并返回成功状态
3. WHEN 测试 Provider 连接时 THEN Provider Service SHALL 验证 API Key 和 Base URL 的有效性
4. WHEN 获取 Provider 列表时 THEN Provider Service SHALL 返回脱敏后的配置信息（隐藏完整 API Key）

### Requirement 6: 任务状态管理测试

**User Story:** As a 用户, I want to 验证任务状态跟踪功能, so that 确保能实时了解笔记生成进度。

#### Acceptance Criteria

1. WHEN 创建新任务时 THEN Task Manager SHALL 生成唯一的 task_id 并返回
2. WHEN 查询任务状态时 THEN Task Manager SHALL 返回当前状态（PENDING/PROCESSING/SUCCESS/FAILED）
3. WHEN 任务完成时 THEN Task Manager SHALL 保存笔记结果并更新状态为 SUCCESS
4. WHEN 任务失败时 THEN Task Manager SHALL 记录错误信息并更新状态为 FAILED
5. WHEN 重试失败任务时 THEN Task Manager SHALL 复用原 task_id 并重置状态为 PENDING

### Requirement 7: 前端功能可用性测试

**User Story:** As a 用户, I want to 验证前端界面的功能完整性, so that 确保用户交互正常。

#### Acceptance Criteria

1. WHEN 前端应用启动时 THEN BiliNote 前端 SHALL 成功加载并显示主界面
2. WHEN 后端服务不可用时 THEN BiliNote 前端 SHALL 显示后端初始化对话框
3. WHEN 提交视频 URL 时 THEN BiliNote 前端 SHALL 发送请求并显示任务进度
4. WHEN 笔记生成完成时 THEN BiliNote 前端 SHALL 渲染 Markdown 内容和思维导图

### Requirement 8: 性能基准测试

**User Story:** As a 开发者, I want to 建立性能基准指标, so that 确保系统在负载下表现稳定。

#### Acceptance Criteria

1. WHEN 测量 API 响应时间时 THEN BiliNote 后端 SHALL 在 500ms 内响应简单查询请求
2. WHEN 测量音频转写性能时 THEN Transcriber 模块 SHALL 记录处理时间与音频时长的比率
3. WHEN 测量笔记生成性能时 THEN Note Generator SHALL 记录从请求到完成的总耗时
4. WHEN 并发请求时 THEN BiliNote 后端 SHALL 正确处理多个同时进行的任务

### Requirement 9: 错误处理和日志测试

**User Story:** As a 开发者, I want to 验证错误处理和日志记录机制, so that 便于问题排查和调试。

#### Acceptance Criteria

1. WHEN 发生业务异常时 THEN BiliNote 后端 SHALL 返回结构化的错误响应（包含错误码和消息）
2. WHEN 发生系统异常时 THEN BiliNote 后端 SHALL 记录完整的异常堆栈到日志
3. WHEN 关键操作执行时 THEN BiliNote 后端 SHALL 记录操作日志（包含时间戳和上下文）
4. WHEN 查看日志时 THEN 日志系统 SHALL 支持按级别（DEBUG/INFO/WARNING/ERROR）过滤

### Requirement 10: 数据库完整性测试

**User Story:** As a 开发者, I want to 验证数据库操作的正确性, so that 确保数据持久化可靠。

#### Acceptance Criteria

1. WHEN 系统首次启动时 THEN 数据库初始化 SHALL 创建所有必需的表结构
2. WHEN 插入 Provider 记录时 THEN 数据库 SHALL 正确保存所有字段并生成唯一 ID
3. WHEN 插入 Model 记录时 THEN 数据库 SHALL 维护与 Provider 的外键关系
4. WHEN 查询历史任务时 THEN 数据库 SHALL 返回按时间排序的任务列表
