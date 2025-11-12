@echo off

REM BiliNote 开发环境一键启动脚本
REM 此脚本将同时启动后端(FastAPI)和前端(React)服务

set "ROOT_DIR=%~dp0"
echo 正在启动 BiliNote 开发环境...

REM 检查是否已安装依赖
if not exist "%ROOT_DIR%\backend\venv" (
    echo 后端虚拟环境不存在，正在创建...
    cd "%ROOT_DIR%\backend"
    python -m venv venv
    echo 正在安装后端依赖...
    call venv\Scripts\activate
    pip install -r requirements.txt
    deactivate
    echo 后端依赖安装完成。
)

REM 启动后端服务
start "BiliNote Backend" cmd /k "cd %ROOT_DIR%\backend && call venv\Scripts\activate && python main.py"

REM 等待后端服务启动
ping 127.0.0.1 -n 3 > nul

REM 检查前端依赖是否已安装
if not exist "%ROOT_DIR%\BillNote_frontend\node_modules" (
    echo 前端依赖不存在，正在安装...
    cd "%ROOT_DIR%\BillNote_frontend"
    npm install
    echo 前端依赖安装完成。
)

REM 启动前端服务
start "BiliNote Frontend" cmd /k "cd %ROOT_DIR%\BillNote_frontend && npm run dev"

echo 开发环境启动完成！
echo 后端服务地址: http://localhost:8000
echo 前端服务地址: http://localhost:5173
pause