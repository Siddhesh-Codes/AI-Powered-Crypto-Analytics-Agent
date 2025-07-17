@echo off
title Crypto Analytics App Launcher
color 0B

echo.
echo ===============================================
echo    🚀 CRYPTO ANALYTICS APP LAUNCHER 🚀  
echo ===============================================
echo.
echo This will start both the backend and frontend.
echo.

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"

echo 1️⃣ Starting AI Backend Server...
echo.
start "AI Backend" cmd /c "cd /d "%BACKEND_DIR%" && RUN_BACKEND.bat"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo 2️⃣ Starting Frontend Development Server...
echo.
start "Frontend" cmd /c "cd /d "%FRONTEND_DIR%" && npm start"

echo.
echo ✅ Both servers are starting!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🤖 Backend:  http://localhost:8000+ (auto-port)
echo 📖 API Docs: http://localhost:8000+/docs
echo.
echo Both windows will open automatically.
echo Close this window when done.
echo.
pause
