@echo off
title Smart Guitar Tab Generator
cd /d "%~dp0"

echo Starting Backend Server...
start /B python app.py

echo Waiting for Server...
timeout /t 3 /nobreak >nul

echo Launching Smart Guitar Tab App...
REM Try Edge first (Native App mode built in to Windows)
start msedge --app="http://localhost:8000" 
if %ERRORLEVEL% neq 0 (
    REM Fallback to Chrome
    start chrome --app="http://localhost:8000"
    if %ERRORLEVEL% neq 0 (
        REM Ultimate Fallback
        start http://localhost:8000
    )
)

echo App is running. Close this window to stop the server later.
