@echo off
title Smart Guitar Tab Generator
cd /d "%~dp0"

echo ============================================
echo   Smart Guitar Tab Generator
echo ============================================
echo.

echo [1/3] Checking and closing port 8000...
set PORT_FOUND=0
for /f "tokens=5" %%P in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Found active process PID %%P. Terminating...
    taskkill /F /PID %%P >nul 2>&1
    set PORT_FOUND=1
)
if "%PORT_FOUND%"=="0" (
    echo Port 8000 is free. Excellent!
) else (
    echo Terminated successfully.
)
echo.

echo [2/3] Activating Python Virtual Environment...
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    echo Virtual environment activated!
) else (
    echo No virtual environment found. Using global Python...
)
echo.

echo [3/3] Starting server...
set LOG_LEVEL=info

REM Open browser silently in background after 2 seconds
powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:8000/v2'"

echo --------------------------------------------
echo   Server is running. Keep this window open!
echo   To stop, close this window or press Ctrl+C
echo --------------------------------------------
echo.

python -u app.py

echo.
echo Server stopped.
pause
