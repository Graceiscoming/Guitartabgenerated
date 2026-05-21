@echo off
title Guitar Tab - Unit Tests
cd /d "%~dp0"

echo.
echo  ============================================
echo    รัน Unit Tests ทั้งหมด (tests/test_*.py)
echo  ============================================
echo.

python -m unittest discover -s tests -p "test_*.py" -v

echo.
if %ERRORLEVEL% equ 0 (
    echo ผ่านทั้งหมด
) else (
    echo มี test ล้มเหลว — ดูรายละเอียดด้านบน
)
echo.
pause
