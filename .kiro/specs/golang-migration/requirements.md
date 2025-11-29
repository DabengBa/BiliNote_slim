# Requirements Document

## Introduction

本文档定义了将 BiliNote 后端从 Python (FastAPI) 迁移到 Go 语言的需求规格。BiliNote 是一个 AI 视频笔记生成工具，支持从 Bilibili、YouTube、抖音等平台下载视频，进行音频转写，并使用 GPT 生成结构化 Markdown 笔记。

### 可行性分析

#### 当前 Python 架构分析

| 模块 | 功能 | 迁移难度 | 说明 |
|------|------|----------|------|
| FastAPI Web 框架 | REST API | ⭐ 低 | Go 有 Gin/Echo/Fiber 等成熟框架 |
| SQLite/SQLAlchemy | 数据持久化 | ⭐ 低 | Go 有 GORM/sqlx 等 ORM |
| OpenAI SDK | GPT 调用 | ⭐ 低 | Go 有官方 openai-go SDK |
| Google Speech-to-Text | 云端音频转写 | ⭐ 低 | Go 官方 SDK，无需本地模型 |
| yt-dlp | YouTube 下载 | ⭐⭐ 中 | 需调用 CLI 或使用 Go 库 |
| 平台下载器 (Bilibili/抖音/快手) | 视频下载 | ⭐⭐ 中 | 需重写爬虫逻辑 |
| FFmpeg 集成 | 音视频处理 | ⭐ 低 | Go 可直接调用 FFmpeg CLI |
| 视频截图/缩略图 | 图像处理 | ⭐ 低 | Go 有 image 标准库 |

#### 迁移策略建议

**推荐方案：完全 Go 重写**

使用 Google Cloud Speech-to-Text API 替代 faster-whisper，实现 100% Go 后端：

1. **Go 单体服务**：处理所有功能 - HTTP API、下载、转写、GPT 调用、数据库
2. **云端转写**：使用 Google Speech-to-Text API，Go 原生 SDK 支持
3. **无 Python 依赖**：单二进制部署

#### 迁移收益

- 更低的内存占用和更快的启动时间
- 更好的并发处理能力
- **单二进制部署，无 Python/ML 依赖**
- 更强的类型安全
- 简化 Docker 镜像（无需 CUDA/PyTorch）

## Glossary

- **BiliNote_Backend**: 使用 Go 语言重写的后端服务
- **Google_Speech_Client**: Google Cloud Speech-to-Text API 客户端
- **Downloader**: 视频/音频下载模块，支持多平台
- **GPT_Client**: OpenAI 兼容 API 客户端
- **Note_Generator**: 笔记生成核心服务
- **Task_Manager**: 异步任务状态管理器
- **Provider**: AI 模型供应商配置

## Requirements

### Requirement 1: HTTP API 服务

**User Story:** As a frontend developer, I want the Go backend to provide the same REST API interface, so that the existing React frontend can work without modification.

#### Acceptance Criteria

1. WHEN a client sends a request to `/api/note/generate` THEN the BiliNote_Backend SHALL accept the request and return a task ID
2. WHEN a client queries `/api/task/{task_id}/status` THEN the BiliNote_Backend SHALL return the current task status in JSON format
3. WHEN a client requests `/api/provider` endpoints THEN the BiliNote_Backend SHALL perform CRUD operations on Provider configurations
4. WHEN a client requests `/api/model` endpoints THEN the BiliNote_Backend SHALL return available AI models for a provider
5. WHEN the server starts THEN the BiliNote_Backend SHALL serve static files from the configured directory

### Requirement 2: 视频/音频下载

**User Story:** As a user, I want to download videos from multiple platforms, so that I can generate notes from various video sources.

#### Acceptance Criteria

1. WHEN a user provides a Bilibili video URL THEN the Downloader SHALL extract video metadata and download audio
2. WHEN a user provides a YouTube video URL THEN the Downloader SHALL use yt-dlp to download audio
3. WHEN a user provides a Douyin video URL THEN the Downloader SHALL parse the share link and download audio
4. WHEN a user provides a local file path THEN the Downloader SHALL read the file directly
5. WHEN download quality is specified THEN the Downloader SHALL select the appropriate bitrate (32/64/128 kbps)
6. IF a download fails THEN the Downloader SHALL return an error with platform-specific error code

### Requirement 3: 音频转写 (Google Speech-to-Text)

**User Story:** As a user, I want my audio to be transcribed to text using Google Cloud, so that GPT can summarize the content.

#### Acceptance Criteria

1. WHEN audio transcription is requested THEN the BiliNote_Backend SHALL upload audio to Google Cloud Storage
2. WHEN audio is uploaded THEN the BiliNote_Backend SHALL call Google Speech-to-Text API with language hints
3. WHEN Google API returns results THEN the BiliNote_Backend SHALL parse word-level timestamps into segments
4. WHEN transcription completes THEN the BiliNote_Backend SHALL cache the result to avoid re-processing
5. IF audio duration exceeds 1 minute THEN the BiliNote_Backend SHALL use asynchronous (LongRunningRecognize) mode
6. IF Google API returns an error THEN the BiliNote_Backend SHALL return a structured error with details

### Requirement 4: GPT 笔记生成

**User Story:** As a user, I want GPT to summarize my video transcript into structured notes, so that I can quickly understand the video content.

#### Acceptance Criteria

1. WHEN transcript segments are provided THEN the GPT_Client SHALL format them with timestamps
2. WHEN a provider configuration is specified THEN the GPT_Client SHALL use the corresponding API key and base URL
3. WHEN screenshot markers are requested THEN the GPT_Client SHALL include Screenshot-[mm:ss] placeholders in the prompt
4. WHEN link markers are requested THEN the GPT_Client SHALL include Link-[mm:ss] placeholders in the prompt
5. WHEN GPT returns markdown THEN the Note_Generator SHALL post-process screenshot and link markers
6. IF GPT API returns an error THEN the GPT_Client SHALL propagate the error with details

### Requirement 5: 任务状态管理

**User Story:** As a user, I want to track the progress of my note generation task, so that I know when it's complete.

#### Acceptance Criteria

1. WHEN a task is created THEN the Task_Manager SHALL assign a unique UUID
2. WHEN task status changes THEN the Task_Manager SHALL persist the status to a JSON file
3. WHEN a task transitions through phases THEN the Task_Manager SHALL record: PARSING → DOWNLOADING → TRANSCRIBING → SUMMARIZING → SAVING → SUCCESS
4. IF a task fails THEN the Task_Manager SHALL record the FAILED status with error message
5. WHEN querying task status THEN the Task_Manager SHALL return the current phase and any error message

### Requirement 6: 数据持久化

**User Story:** As a user, I want my provider configurations and task history to be saved, so that I don't lose my settings.

#### Acceptance Criteria

1. WHEN the server starts THEN the BiliNote_Backend SHALL initialize SQLite database with required tables
2. WHEN a provider is created THEN the BiliNote_Backend SHALL store it with encrypted API key
3. WHEN a task completes THEN the BiliNote_Backend SHALL record video_id, platform, and task_id
4. WHEN querying providers THEN the BiliNote_Backend SHALL mask API keys in responses (show only last 4 characters)
5. WHEN default providers are needed THEN the BiliNote_Backend SHALL seed from builtin_providers.json

### Requirement 7: 截图生成

**User Story:** As a user, I want screenshots inserted at key moments in my notes, so that I have visual references.

#### Acceptance Criteria

1. WHEN a Screenshot-[mm:ss] marker is found THEN the Note_Generator SHALL extract a frame at that timestamp
2. WHEN extracting a frame THEN the Note_Generator SHALL use FFmpeg to generate a JPEG image
3. WHEN a screenshot is generated THEN the Note_Generator SHALL save it to the static directory
4. WHEN replacing markers THEN the Note_Generator SHALL use the correct static URL path
5. IF video file is unavailable THEN the Note_Generator SHALL skip screenshot generation gracefully

### Requirement 8: 配置管理

**User Story:** As a system administrator, I want to configure the backend via environment variables, so that I can deploy it in different environments.

#### Acceptance Criteria

1. WHEN the server starts THEN the BiliNote_Backend SHALL read configuration from .env file
2. WHEN BACKEND_PORT is set THEN the BiliNote_Backend SHALL listen on that port
3. WHEN TRANSCRIBER_URL is set THEN the BiliNote_Backend SHALL use that URL for transcription service
4. WHEN DATA_DIR is set THEN the BiliNote_Backend SHALL use that directory for downloads
5. WHEN OUT_DIR is set THEN the BiliNote_Backend SHALL use that directory for screenshots

### Requirement 9: 错误处理与日志

**User Story:** As a developer, I want comprehensive error handling and logging, so that I can debug issues effectively.

#### Acceptance Criteria

1. WHEN an error occurs THEN the BiliNote_Backend SHALL return a structured JSON error response
2. WHEN processing a request THEN the BiliNote_Backend SHALL log request details at INFO level
3. WHEN an exception is caught THEN the BiliNote_Backend SHALL log stack trace at ERROR level
4. WHEN a task fails THEN the BiliNote_Backend SHALL include the error message in task status
5. WHEN the server starts THEN the BiliNote_Backend SHALL log configuration summary

### Requirement 10: Google Cloud 集成

**User Story:** As a system administrator, I want to configure Google Cloud credentials, so that the transcription service works correctly.

#### Acceptance Criteria

1. WHEN GOOGLE_APPLICATION_CREDENTIALS is set THEN the BiliNote_Backend SHALL use that service account file
2. WHEN GCS_BUCKET is set THEN the BiliNote_Backend SHALL use that bucket for audio uploads
3. WHEN audio is uploaded to GCS THEN the BiliNote_Backend SHALL set appropriate lifecycle rules for cleanup
4. WHEN transcription completes THEN the BiliNote_Backend SHALL delete the temporary audio file from GCS
5. IF credentials are invalid THEN the BiliNote_Backend SHALL return a configuration error at startup
