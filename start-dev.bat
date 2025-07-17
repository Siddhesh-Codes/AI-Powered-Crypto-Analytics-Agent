@echo off
echo Starting AI-Powered Crypto Analytics Application...

echo.
echo Starting Backend Server...
cd backend
python simple_main.py

echo.
echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend Server...
start cmd /k "cd frontend && npm start"

echo.
echo Both servers should be starting up!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Press any key to exit...
pause >nul
