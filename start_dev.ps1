# BiliNote 开发环境一键启动脚本 (PowerShell 版本)
# 此脚本将同时启动后端(FastAPI)和前端(React)服务

Write-Host "正在启动 BiliNote 开发环境..." -ForegroundColor Green

# 获取脚本所在目录
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# 检查是否已安装后端依赖
if (-not (Test-Path "$ROOT_DIR\backend\venv")) {
    Write-Host "后端虚拟环境不存在，正在创建..." -ForegroundColor Yellow
    Set-Location "$ROOT_DIR\backend"
    python -m venv venv
    Write-Host "正在安装后端依赖..." -ForegroundColor Yellow
    & "$ROOT_DIR\backend\venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
    deactivate
    Write-Host "后端依赖安装完成。" -ForegroundColor Green
}

# 启动后端服务
Write-Host "正在启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command Set-Location '$ROOT_DIR\backend'; & '.\venv\Scripts\Activate.ps1'; python main.py"

# 等待后端服务启动
Start-Sleep -Seconds 3

# 检查前端依赖是否已安装
if (-not (Test-Path "$ROOT_DIR\BillNote_frontend\node_modules")) {
    Write-Host "前端依赖不存在，正在安装..." -ForegroundColor Yellow
    Set-Location "$ROOT_DIR\BillNote_frontend"
    npm install
    Write-Host "前端依赖安装完成。" -ForegroundColor Green
}

# 启动前端服务
Write-Host "正在启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command Set-Location '$ROOT_DIR\BillNote_frontend'; npm run dev"

Write-Host "开发环境启动完成！" -ForegroundColor Green
Write-Host "后端服务地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "前端服务地址: http://localhost:5173" -ForegroundColor Cyan

Read-Host "按 Enter 键退出..."