#!/bin/bash
# 同时启动前后端开发服务器 (模拟生产环境)
# 使用方式: ./dev.sh

echo "========================================"
echo "  BiliNote Dev Environment"
echo "========================================"
echo

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "[WARN] .env 文件不存在，正在从 .env.example 复制..."
    cp .env.example .env
fi

# 清理函数
cleanup() {
    echo ""
    echo "[INFO] 正在停止服务..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# 启动后端
echo "[INFO] 启动后端服务 (端口 8483)..."
cd backend && python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "[INFO] 启动前端服务 (端口 3015)..."
cd BillNote_frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  服务已启动:"
echo "  - 后端: http://localhost:8483"
echo "  - 前端: http://localhost:3015"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待子进程
wait
