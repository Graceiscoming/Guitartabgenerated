@echo off
chcp 65001 >nul
title หยุด Guitar Tab Server
cd /d "%~dp0"

echo กำลังหา process ที่ใช้ port 8000...
set FOUND=0

for /f "tokens=5" %%P in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo ปิด PID %%P
    taskkill /F /PID %%P >nul 2>&1
    set FOUND=1
)

if "%FOUND%"=="0" (
    echo ไม่พบเซิร์ฟเวอร์ที่รันอยู่บน port 8000
) else (
    echo เสร็จแล้ว — ปิดเซิร์ฟเวอร์ที่ค้างอยู่แล้ว
)

echo.
pause
