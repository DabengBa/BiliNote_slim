# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

BiliNote v1.8.1 是一个开源的 AI 视频笔记生成工具，支持通过哔哩哔哩、YouTube等视频链接，自动提取内容并生成结构清晰、重点明确的 Markdown 格式笔记。

## 技术栈

- **后端**: FastAPI (Python) + SQLite + SQLAlchemy
- **前端**: React 19 + TypeScript + Vite + TailwindCSS
- **AI 模型**: OpenAI / DeepSeek / Qwen / Groq
- **音频转录**: Fast-Whisper / BCUT / MLX-Whisper / Groq
- **视频下载**: yt-dlp + 自定义下载器
- **部署**: Docker + Docker Compose + Nginx
- **桌面应用**: Tauri (Rust + 前端)

## 目录结构

```
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── core/              # 核心配置 (config.py)
│   │   ├── db/                # 数据库层 (SQLite + SQLAlchemy)
│   │   │   ├── models/        # 数据模型
│   │   │   ├── dao/           # 数据访问对象
│   │   │   └── engine.py      # 数据库引擎
│   │   ├── routers/           # API 路由
│   │   │   ├── note.py        # 笔记相关 API
│   │   │   ├── provider.py    # AI 模型提供商 API
│   │   │   ├── model.py       # 模型管理 API
│   │   │   └── config.py      # 配置管理 API
│   │   ├── services/          # 业务服务层
│   │   ├── gpt/               # AI 模型集成
│   │   │   ├── base.py        # 基础接口
│   │   │   ├── openai_gpt.py  # OpenAI 实现
│   │   │   ├── deepseek_gpt.py
│   │   │   ├── qwen_gpt.py
│   │   │   └── gpt_factory.py # 工厂模式
│   │   ├── transcriber/       # 音频转录服务
│   │   │   ├── base.py        # 转录器基类
│   │   │   ├── whisper.py     # Fast-Whisper 实现
│   │   │   ├── groq.py        # Groq 转录
│   │   │   └── transcriber_provider.py
│   │   ├── downloaders/       # 视频下载器
│   │   │   ├── bilibili_downloader.py
│   │   │   ├── youtube_downloader.py
│   │   │   ├── local_downloader.py
│   │   │   └── base.py        # 下载器基类
│   │   ├── utils/             # 工具函数
│   │   └── validators/        # 数据验证
│   ├── main.py                # 后端入口
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile             # CPU 版本
│   ├── Dockerfile.gpu         # GPU 版本 (CUDA)
│   ├── build.sh               # Linux/Mac 打包脚本
│   └── build.bat              # Windows 打包脚本
│
├── BillNote_frontend/          # React 前端
│   ├── src/
│   │   ├── components/        # React 组件
│   │   │   ├── ui/            # UI 基础组件
│   │   │   ├── Form/          # 表单组件
│   │   │   ├── Icons/         # 图标组件
│   │   │   └── Lottie/        # 动画组件
│   │   ├── pages/             # 页面组件
│   │   │   ├── HomePage/      # 首页
│   │   │   └── SettingPage/   # 设置页
│   │   ├── services/          # API 服务
│   │   ├── store/             # Zustand 状态管理
│   │   ├── hooks/             # 自定义 Hooks
│   │   ├── lib/               # 库函数
│   │   ├── utils/             # 工具函数
│   │   └── types/             # TypeScript 类型定义
│   ├── src-tauri/             # Tauri 桌面应用
│   ├── package.json           # npm 依赖
│   ├── vite.config.ts         # Vite 配置
│   ├── tailwind.config.cjs    # TailwindCSS 配置
│   ├── tsconfig.json          # TypeScript 配置
│   └── Dockerfile
│
├── nginx/                      # Nginx 配置
│   └── default.conf           # 反向代理配置
├── docker-compose.yml          # Docker Compose (CPU)
├── docker-compose.gpu.yml      # Docker Compose (GPU)
├── .env.example               # 环境变量模板
└── README.md                  # 项目文档
```

## 常用命令

### 开发环境

**后端开发**:
```bash
cd backend
pip install -r requirements.txt
python main.py
# 服务启动在 http://localhost:8483
```

**前端开发**:
```bash
cd BillNote_frontend
pnpm install
pnpm dev
# 服务启动在 http://localhost:3015
```

### Docker 部署

**CPU 版本**:
```bash
docker-compose up -d
# 访问 http://localhost:3015
```

**GPU 版本** (需要 NVIDIA GPU):
```bash
docker-compose -f docker-compose.gpu.yml up -d
```

**停止服务**:
```bash
docker-compose down
```

### 构建打包

**桌面应用打包** (将后端打包为可执行文件):
```bash
# Linux/Mac
cd backend
./build.sh

# Windows
cd backend
build.bat
```

### 代码检查

**前端**:
```bash
cd BillNote_frontend
pnpm lint
```

## 环境变量

主要环境变量在 `.env.example` 中定义：

```bash
# 端口配置
BACKEND_PORT=8483          # 后端端口
FRONTEND_PORT=3015         # 前端端口
APP_PORT=3015              # Docker 部署端口

# API 配置
VITE_API_BASE_URL=http://127.0.0.1:8483
VITE_SCREENSHOT_BASE_URL=http://127.0.0.1:8483/static/screenshots

# 转录器配置
TRANSCRIBER_TYPE=fast-whisper  # fast-whisper/bcut/mlx-whisper(仅Apple平台)/groq
WHISPER_MODEL_SIZE=base        # 模型大小
GROQ_TRANSCRIBER_MODEL=whisper-large-v3-turbo

# 目录配置
NOTE_OUTPUT_DIR=note_results
DATA_DIR=data
IMAGE_BASE_URL=/static/screenshots
```

## 核心架构

### 后端架构 (FastAPI)

1. **路由层** (`app/routers/`): 处理 HTTP 请求
2. **服务层** (`app/services/`): 业务逻辑处理
3. **数据层** (`app/db/`): 数据持久化 (SQLite)
4. **AI 层** (`app/gpt/`): 多模型 AI 集成
5. **转录层** (`app/transcriber/`): 音频转文字
6. **下载层** (`app/downloaders/`): 多平台视频下载

### 前端架构 (React + Vite)

1. **页面层** (`src/pages/`): 路由页面
2. **组件层** (`src/components/`): 可复用组件
3. **服务层** (`src/services/`): API 调用
4. **状态层** (`src/store/`): Zustand 状态管理
5. **Hooks 层** (`src/hooks/`): 业务逻辑复用

### 核心工作流程

1. 用户在前端输入视频链接
2. 前端调用 `/api/note/generate` 接口
3. 后端根据视频平台选择对应下载器
4. 下载器下载视频并提取音频
5. 转录器将音频转为文字
6. GPT 模型分析文字并生成结构化笔记
7. 返回 Markdown 格式笔记给前端

## 依赖项

### 必装软件

- **Python 3.8+**: 后端运行环境
- **Node.js 18+** & **pnpm**: 前端开发
- **FFmpeg**: 音频处理 (必须安装并加入 PATH)

```bash
# Mac
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载安装
```

### 可选软件

- **CUDA 11.8+**: GPU 加速 (需要 NVIDIA GPU)
- **Docker & Docker Compose**: 容器化部署
- **Rust**: 桌面应用打包

## API 文档

启动后端服务后，访问 `http://localhost:8483/docs` 查看完整的 FastAPI 自动生成文档。

主要 API 端点:
- `POST /api/note/generate`: 生成视频笔记
- `GET /api/provider`: 获取 AI 模型提供商列表
- `POST /api/model`: 配置 AI 模型
- `GET /api/config`: 获取配置
- `POST /api/config`: 更新配置

## 部署注意事项

1. **FFmpeg**: 必须安装并配置到系统 PATH
2. **端口占用**: 确保 8483 和 3015 端口未被占用
3. **CUDA**: GPU 版本需要 NVIDIA 驱动和 CUDA Toolkit
4. **文件权限**: Docker 部署需要写入权限用于生成截图
5. **网络**: 生产环境需要配置防火墙开放 3015 端口

## 开发规范

- **后端**: 使用 Pydantic 进行数据验证，SQLAlchemy ORM
- **前端**: 使用 TypeScript 严格模式，React Hooks + Zustand
- **代码风格**: 后端遵循 PEP 8，前端使用 ESLint + Prettier
- **提交信息**: 使用 conventional commits 格式

## 常见问题

**Q: FFmpeg 找不到**
A: 确保 FFmpeg 已安装并添加到系统 PATH 环境变量

**Q: 音频转录失败**
A: 检查 FFmpeg 是否正确安装，或尝试切换转录器类型 (fast-whisper/bcut/groq)

**Q: GPU 加速不生效**
A: 确保安装了 CUDA 版本的 requirements，使用 `Dockerfile.gpu` 构建

**Q: 桌面应用打包失败**
A: 检查 Rust 环境，确保 PyInstaller 版本兼容

## Debug 经验总结

### 前端无法访问后端 API 的问题排查

#### 问题症状
后端服务已启动并能通过 curl 正常访问，但前端页面显示网络错误，无法连接到后端。

#### 排查步骤

1. **检查 API 基础路径配置**
   - 确认前端环境变量 `VITE_API_BASE_URL` 设置是否正确
   - 验证后端路由是否需要 `/api` 前缀

2. **检查代理配置**
   - 审查 `vite.config.ts` 中的代理设置
   - 确保代理目标地址与后端服务地址匹配
   - 避免路径中的重复前缀问题（如 `/api/api/sys_check`）

3. **检查 CORS 配置**
   - 验证后端 `main.py` 中的 CORS 配置是否允许前端域名访问
   - 特别注意开发环境中的不同端口（如 3015、5173 等）

4. **添加调试日志**
   - 在前端请求工具中添加环境变量和请求 URL 日志
   - 在 API 调用钩子中添加详细的请求和错误日志
   - 使用浏览器开发者工具查看网络请求详情

#### 解决方案

1. **修复环境变量配置**
   ```
   # .env.development
   VITE_API_BASE_URL=http://localhost:8000/api  # 确保包含 /api 前缀
   ```

2. **修正代理配置**
   ```typescript
   // vite.config.ts
   server: {
     proxy: {
       '/api': {
         target: 'http://localhost:8000',  // 不包含 /api 前缀
         changeOrigin: true,
         // 不需要 rewrite
       },
       '/static': {
         target: 'http://localhost:8000',
         changeOrigin: true,
       },
     },
   }
   ```

3. **更新 CORS 配置**
   ```python
   # main.py
   origins = [
       "http://localhost",
       "http://127.0.0.1",
       "http://tauri.localhost",
       "http://localhost:3015",  # 添加前端开发端口
       "http://localhost:5173",  # 添加可能的 Vite 默认端口
       "http://127.0.0.1:3015",
       "http://127.0.0.1:5173",
   ]
   ```

4. **添加有效的调试日志**
   - 在 `request.ts` 中打印环境变量和实际请求 URL
   - 在 API 调用钩子中记录请求状态、错误类型和重试信息

#### 经验教训

1. **环境变量与代理配置的协同工作**
   - 当同时使用环境变量设置 API 地址和代理配置时，要特别注意路径前缀的重复问题
   - 理解代理的工作原理：代理会将 `/api` 请求转发到目标地址，不要在目标地址中重复包含 `/api`

2. **CORS 配置的完整性**
   - 开发环境中，前端可能在不同端口运行（Vite 默认 5173，自定义配置可能为 3015 等）
   - 确保 CORS 配置包含所有可能的前端来源

3. **系统性的调试方法**
   - 从网络层开始，逐步排查前端请求、代理转发、后端接收的完整链路
   - 使用 curl 等工具直接测试后端 API，排除后端问题
   - 在关键节点添加日志，清晰展示请求的转换过程

4. **配置管理的最佳实践**
   - 保持配置的一致性，特别是在前后端分离架构中
   - 为不同环境（开发、测试、生产）创建清晰的配置文档
   - 使用自动化测试验证 API 的可访问性
