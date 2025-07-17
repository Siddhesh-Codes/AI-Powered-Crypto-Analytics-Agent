@echo off
echo Checking what processes are using port 8000...
echo.

netstat -ano | findstr ":8000"

echo.
echo If you see any processes above, you can kill them with:
echo taskkill /PID [PID_NUMBER] /F
echo.
echo Or just run start_backend.bat which will automatically use a different port.
echo.

pause
