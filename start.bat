@echo off
chcp 65001 >nul
echo ========================================
echo   FinDeep - AI多智能体深度研报系统
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

:: 检查 .env
if not exist .env (
    echo [错误] 未找到 .env 文件，请复制 .env.example 为 .env 并填入API Key
    pause
    exit /b 1
)

echo [1/4] 安装后端依赖...
cd backend
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 后端依赖安装失败
    pause
    exit /b 1
)
echo       后端依赖安装完成

echo [2/4] 安装前端依赖...
cd ..\frontend
call npm install --silent
if errorlevel 1 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
)
echo       前端依赖安装完成

echo [3/4] 启动后端服务 (端口 8000)...
cd ..\backend
start "FinDeep-Backend" cmd /c "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo       后端已启动: http://localhost:8000

echo [4/4] 启动前端服务 (端口 3000)...
cd ..\frontend
start "FinDeep-Frontend" cmd /c "npx next dev --port 3000"
echo       前端已启动: http://localhost:3000

echo.
echo ========================================
echo   启动完成！
echo   打开浏览器访问 http://localhost:3000
echo ========================================
echo.
echo 按任意键关闭此窗口（不影响服务运行）
pause >nul
