@echo off
setlocal enabledelayedexpansion

set PROJECT_ROOT=%~dp0
set BACKEND_DIR=%PROJECT_ROOT%backend
set FRONTEND_DIR=%PROJECT_ROOT%frontend

echo ============================================
echo   BlackBagTest Dev - One Click Start
echo ============================================
echo.

REM ===== Backend checks =====
if not exist "%BACKEND_DIR%\manage.py" (
    echo [ERROR] manage.py not found: %BACKEND_DIR%\manage.py
    pause
    exit /b 1
)

if not exist "%BACKEND_DIR%\.venv\Scripts\activate.bat" (
    echo [SETUP] Backend venv not found, creating...
    pushd "%BACKEND_DIR%"
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Check Python installed.
        popd
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    echo [SETUP] Installing backend deps from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] pip install failed. Fix manually:
        echo   cd backend ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
        popd
        pause
        exit /b 1
    )
    popd
    echo [SETUP] Backend venv ready.
    echo.
)

REM ===== Frontend checks =====
set VUE_CLI=%FRONTEND_DIR%\node_modules\.bin\vue-cli-service.cmd
if not exist "%VUE_CLI%" (
    echo [SETUP] Frontend deps missing or incomplete, installing...
    pushd "%FRONTEND_DIR%"
    where npm >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] npm not found. Install Node.js first.
        popd
        pause
        exit /b 1
    )
    echo [SETUP] Running: npm install --legacy-peer-deps
    call npm install --legacy-peer-deps --no-audit --no-fund --registry=https://registry.npmmirror.com
    if errorlevel 1 (
        echo [ERROR] npm install failed. Retry manually:
        echo   cd frontend ^&^& npm install --legacy-peer-deps
        popd
        pause
        exit /b 1
    )
    if not exist "%VUE_CLI%" (
        echo [ERROR] vue-cli-service still missing after install.
        echo Try: rmdir /s /q node_modules then rerun npm install
        popd
        pause
        exit /b 1
    )
    popd
    echo [SETUP] Frontend deps ready.
    echo.
)

REM ===== Start services =====
set VENV_PY=%BACKEND_DIR%\.venv\Scripts\python.exe

echo [1/3] Starting Backend Uvicorn (port 8000)...
start "BlackBagTest - Backend (8000)" cmd /k "cd /d "%BACKEND_DIR%" && set RUN_ENV=dev && "%VENV_PY%" -m uvicorn black_bag.asgi:application --host 0.0.0.0 --port 8000"

echo [2/3] Starting Q Worker (async tasks)...
start "BlackBagTest - Q Worker" cmd /k "cd /d "%BACKEND_DIR%" && "%VENV_PY%" manage.py qcluster"

echo [3/3] Starting Frontend Vue (port 8080)...
start "BlackBagTest - Frontend (8080)" cmd /k "cd /d "%FRONTEND_DIR%" && npm run serve"

echo.
echo ============================================
echo   All services started in new windows
echo   - Backend:  http://127.0.0.1:8000
echo   - Frontend: http://127.0.0.1:8080
echo   - Q Worker: async task processor
echo ============================================
echo.

REM Redis 是 WebSocket channel layer 的依赖，本地需确保 Redis(127.0.0.1:6379)运行
where redis-server >nul 2>nul
if %errorlevel%==0 (
    echo [NOTE] WebSocket 推送依赖 Redis，如未启动请另行运行: redis-server
) else (
    echo [WARN] 未检测到 redis-server，WebSocket 实时推送将不可用!
    echo        请安装并启动 Redis(Windows 可用 Memurai / Docker)。
)

echo.
echo Close the corresponding window to stop each service.
echo Q Worker needs restart after backend code changes.
echo.
pause
