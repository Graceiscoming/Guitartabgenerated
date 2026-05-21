@echo off
chcp 65001 >nul
title Guitar Tab - Unit Tests
cd /d "%~dp0"

echo.
echo  ============================================
echo    Guitar Tab - Test Suite (pretty output)
echo  ============================================
echo.

python -c "import pytest" 2>nul
if errorlevel 1 (
    echo  ติดตั้ง dependencies สำหรับ test...
    pip install -r requirements-dev.txt -q
    echo.
)

python run_tests.py

echo.
if %ERRORLEVEL% equ 0 (
    echo  เสร็จสิ้น — ผ่านทั้งหมด
) else (
    echo  มี test ล้มเหลว
)
echo.
pause
exit /b %ERRORLEVEL%
