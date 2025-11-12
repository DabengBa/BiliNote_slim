<div style="display: flex; justify-content: center; align-items: center; gap: 10px;
">
    <p align="center">
  <img src="./doc/icon.svg" alt="BiliNote Banner" width="50" height="50"  />
</p>
<h1 align="center" > BiliNote v1.8.1</h1>
</div>

<p align="center"><i>AI 视频笔记生成工具 让 AI 为你的视频做笔记</i></p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" />
  <img src="https://img.shields.io/badge/frontend-react-blue" />
  <img src="https://img.shields.io/badge/backend-fastapi-green" />
  <img src="https://img.shields.io/badge/GPT-openai%20%7C%20deepseek%20%7C%20qwen-ff69b4" />
  <img src="https://img.shields.io/badge/docker-compose-blue" />
  <img src="https://img.shields.io/badge/status-active-success" />
  <img src="https://img.shields.io/github/stars/jefferyhcool/BiliNote?style=social" />
</p>



## ✨ 项目简介

BiliNote 是一个开源的 AI 视频笔记助手，支持通过哔哩哔哩、YouTube等视频链接，自动提取内容并生成结构清晰、重点明确的 Markdown 格式笔记。支持插入截图、原片跳转等功能。
## 📝 使用文档
详细文档可以查看[这里](https://docs.bilinote.app/)

## 体验地址
可以通过访问 [这里](https://www.bilinote.app/) 进行体验，速度略慢，不支持长视频。
## 📦 Windows 打包版
本项目提供了 Windows 系统的 exe 文件，可在[release](https://github.com/JefferyHcool/BiliNote/releases/tag/v1.1.1)进行下载。**注意一定要在没有中文路径的环境下运行。**


## 🔧 功能特性

- 支持多平台：Bilibili、YouTube、本地视频
- 支持返回笔记格式选择
- 支持笔记风格选择
- 支持多模态视频理解
- 支持多版本记录保留
- 支持自行配置 GPT 大模型
- 本地模型音频转写（支持 Fast-Whisper）
- GPT 大模型总结视频内容
- 自动生成结构化 Markdown 笔记
- 可选插入截图（自动截取）
- 可选内容跳转链接（关联原视频）
- 任务记录与历史回看

## 📸 截图预览
![screenshot](./doc/image1.png)
![screenshot](./doc/image3.png)
![screenshot](./doc/image.png)
![screenshot](./doc/image4.png)
![screenshot](./doc/image5.png)

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/JefferyHcool/BiliNote.git
cd BiliNote
mv .env.example .env
```

### 2. 配置环境变量

编辑 `.env` 文件，配置必要的环境变量：

```bash
# 后端配置
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置（默认使用SQLite，无需额外配置）

# 模型配置
# OpenAI API 配置（使用OpenAI模型时需要）
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=your_api_base_url

# 本地模型配置（使用本地模型时需要）
WHISPER_MODEL=base  # 可选：tiny, base, small, medium, large
```

### 3. 启动后端（FastAPI）

#### 方式一：直接启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 方式二：使用虚拟环境启动（推荐）

```bash
# Windows
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

# macOS/Linux
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 4. 启动前端（Vite + React）

```bash
cd BillNote_frontend
# 安装依赖
pnpm install  # 或 npm install 或 yarn install
# 启动开发服务器
pnpm dev  # 或 npm run dev 或 yarn dev
```

访问：`http://localhost:5173`

### 5. 使用 Docker 启动（推荐）

在项目根目录下执行：

```bash
docker-compose up -d
```

访问：`http://localhost:8080`

### 6. 一键启动开发环境（推荐用于本地调试）

为了方便本地调试，我们提供了一键启动脚本，可以同时启动前后端服务：

#### Windows 用户

##### 方法一：使用批处理脚本（适用于命令提示符和 PowerShell）

在项目根目录下双击执行：

```bash
start_dev.bat
```

或者在命令提示符(cmd)中运行：

```bash
./start_dev.bat
```

在 PowerShell 中运行：

```bash
.\start_dev.bat
```

##### 方法二：使用 PowerShell 脚本（推荐用于 PowerShell 用户）

这是专门为 PowerShell 环境优化的脚本，已测试可正常工作：

在项目根目录的 PowerShell 中运行：

```bash
.\start_dev.ps1
```

**注意**：如果遇到执行策略限制，可以先运行以下命令：

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

这将允许在当前 PowerShell 会话中运行本地脚本，不会影响系统的整体执行策略。

#### macOS/Linux 用户

首先赋予脚本执行权限：

```bash
chmod +x start_dev.sh
```

然后在项目根目录下执行：

```bash
./start_dev.sh
```

脚本功能：
- 自动检查并创建后端虚拟环境
- 自动安装前后端依赖（如果不存在）
- 同时启动后端和前端服务
- 显示服务地址信息

**注意**：首次运行脚本会安装依赖，可能需要一些时间。后续运行将直接启动服务。

## ⚙️ 依赖说明
### 🎬 FFmpeg
本项目依赖 ffmpeg 用于音频处理与转码，必须安装：
```bash
# Mac (brew)
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
# 请从官网下载安装：https://ffmpeg.org/download.html
```
> ⚠️ 若系统无法识别 ffmpeg，请将其加入系统环境变量 PATH

### 🚀 CUDA 加速（可选）
若你希望更快地执行音频转写任务，可使用具备 NVIDIA GPU 的机器，并启用 fast-whisper + CUDA 加速版本：

具体 `fast-whisper` 配置方法，请参考：[fast-whisper 项目地址](http://github.com/SYSTRAN/faster-whisper#requirements)

### 🐳 使用 Docker 一键部署

确保你已安装 Docker 和 Docker Compose：

[docker 部署](https://github.com/JefferyHcool/bilinote-deploy/blob/master/README.md)

## 🧠 TODO

- [x] 支持多平台视频（Bilibili、YouTube、本地视频）
- [x] 支持前端设置切换 AI 模型切换、语音转文字模型
- [x] AI 摘要风格自定义（学术风、口语风、重点提取等）
- [ ] 笔记导出为 PDF / Word / Notion
- [x] 加入更多模型支持
- [x] 加入更多音频转文本模型支持

### Contact and Join-联系和加入社区
- BiliNote 交流QQ群：785367111
- BiliNote 交流微信群:
  
  <img src="doc/wechat.png" alt="wechat" style="zoom:33%;" />



## 🔎代码参考
- 本项目早期曾参考以下项目的设计思路（已移除相关功能）：

## 📜 License

MIT License

---

💬 你的支持与反馈是我持续优化的动力！欢迎 PR、提 issue、Star ⭐️
## Buy Me a Coffee / 捐赠
如果你觉得项目对你有帮助，考虑支持我一下吧
<div style='display:inline;'>
    <img width='30%' src='https://common-1304618721.cos.ap-chengdu.myqcloud.com/8986c9eb29c356a0cfa3d470c23d3b6.jpg'/>
    <img width='30%' src='https://common-1304618721.cos.ap-chengdu.myqcloud.com/2a049ea298b206bcd0d8b8da3219d6b.jpg'/>
</div>

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JefferyHcool/BiliNote&type=Date)](https://www.star-history.com/#JefferyHcool/BiliNote&Date)
