@echo off
title Guitar Tab - Static Tests
cd /d "%~dp0"

echo.
echo  ============================================
echo    Guitar Tab - Static Testing Suite
echo  ============================================
echo.

python -c "import flake8" 2>nul
if errorlevel 1 (
    echo  Installing dependencies for static test...
    pip install -r requirements-dev.txt -q
    echo.
)

python run_static_tests.py

echo.
pause
