@echo off
REM 同时启动前后端开发服务器 (模拟生产环境)
REM 使用方式: dev.bat

echo ========================================
echo   BiliNote Dev Environment
echo ========================================
echo.

REM 检查 .env 文件
if not exist ".env" (
    echo [WARN] .env 文件不存在，正在从 .env.example 复制...
    copy .env.example .env
)

REM 检查前端依赖
if not exist "BillNote_frontend\node_modules" (
    echo [INFO] 前端依赖未安装，正在安装...
    cd BillNote_frontend
    call npm install
    cd ..
)

REM 启动后端 (新窗口)
echo [INFO] 启动后端服务 (端口 8483)...
start "BiliNote Backend" cmd /k "cd backend && python main.py"

REM 等待后端启动
timeout /t 3 /nobreak > nul

REM 启动前端 (新窗口)
echo [INFO] 启动前端服务 (端口 3015)...
start "BiliNote Frontend" cmd /k "cd BillNote_frontend && npm run dev"

echo.
echo ========================================
echo   服务已启动:
echo   - 后端: http://localhost:8483
echo   - 前端: http://localhost:3015
echo ========================================
echo.
echo 按任意键关闭此窗口 (服务会继续运行)
pause > nul
