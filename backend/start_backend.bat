@echo off
echo Starting Crypto Analytics AI Backend...
echo.

cd /d "c:\Users\lenovo\OneDrive\Desktop\Final Year Project\AI Powered Crypto Application\backend"

echo Installing/updating required packages...
C:/Users/lenovo/AppData/Local/Programs/Python/Python311/python.exe -m pip install fastapi uvicorn python-jose passlib python-multipart requests groq transformers python-dotenv

echo.
echo Setting up Groq API key...
set GROQ_API_KEY=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
echo ✅ Groq API key configured

echo.
echo Checking for available ports...

echo Starting simple backend server...
echo If port 8000 is busy, the server will try ports 8001, 8002, etc.
echo.

C:/Users/lenovo/AppData/Local/Programs/Python/Python311/python.exe simple_backend.py

echo.
echo Backend server has stopped.
pause
