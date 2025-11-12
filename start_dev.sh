#!/bin/bash

# BiliNote 开发环境一键启动脚本
# 此脚本将同时启动后端(FastAPI)和前端(React)服务

echo "正在启动 BiliNote 开发环境..."

# 获取脚本所在目录
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查是否已安装后端依赖
if [ ! -d "${ROOT_DIR}/backend/venv" ]; then
    echo "后端虚拟环境不存在，正在创建..."
    cd "${ROOT_DIR}/backend"
    python3 -m venv venv
    echo "正在安装后端依赖..."
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    echo "后端依赖安装完成。"
fi

# 启动后端服务
osascript -e "tell application \"Terminal\" to do script \"cd ${ROOT_DIR}/backend && source venv/bin/activate && python main.py\""

# 等待后端服务启动
sleep 2

# 检查前端依赖是否已安装
if [ ! -d "${ROOT_DIR}/BillNote_frontend/node_modules" ]; then
    echo "前端依赖不存在，正在安装..."
    cd "${ROOT_DIR}/BillNote_frontend"
    npm install
    echo "前端依赖安装完成。"
fi

# 启动前端服务
osascript -e "tell application \"Terminal\" to do script \"cd ${ROOT_DIR}/BillNote_frontend && npm run dev\""

echo "开发环境启动完成！"
echo "后端服务地址: http://localhost:8000"
echo "前端服务地址: http://localhost:5173"