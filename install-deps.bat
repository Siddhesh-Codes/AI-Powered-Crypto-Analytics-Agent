@echo off
echo Installing all dependencies...

echo.
echo [1/3] Installing root dependencies...
call npm install

echo.
echo [2/3] Installing frontend dependencies...
cd ..\frontend
call npm install
cd ..

echo.
echo [3/3] Installing backend dependencies...
cd backend
call pip install fastapi uvicorn python-dotenv pydantic-settings
cd ..

echo.
echo ✅ All dependencies installed!
echo.
echo To start the application, run: npm run dev
pause
