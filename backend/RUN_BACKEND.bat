@echo off
title Crypto AI Backend Server
color 0A

echo.
echo ===============================================
echo    🚀 CRYPTO AI BACKEND SERVER 🚀
echo ===============================================
echo.

cd /d "%~dp0"

echo 📦 Installing packages...
python -m pip install fastapi uvicorn requests groq --quiet

echo.
echo 🚀 Starting AI Backend Server...
echo.
echo Backend will automatically find an available port:
echo   - Trying 8000, 8001, 8002, 8003, 8080...
echo   - Frontend will auto-connect to the right port
echo.

python simple_backend.py

echo.
echo ⚠️ Backend server has stopped.
echo.
pause
