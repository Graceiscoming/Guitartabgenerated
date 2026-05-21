@echo off
title Smart Guitar Tab Generator
cd /d "%~dp0"

echo.
echo  ============================================
echo    Guitar Tab - เซิร์ฟเวอร์จะทำงานเมื่อหน้าต่างนี้เปิดอยู่
echo    ปิดหน้าต่างนี้ หรือ กด Ctrl+C  =  หยุดเซิร์ฟเวอร์
echo  ============================================
echo.

REM เปิดเบราว์เซอร์หลังรอ ~2 วินาที (ไม่บล็อกเซิร์ฟเวอร์)
start "" cmd /c "ping -n 3 127.0.0.1 >nul && start http://localhost:8000/v2"

REM รันเซิร์ฟเวอร์หน้าต่างนี้ (ไม่ใช้ start /B — ปิดหน้าต่างแล้วเซิร์ฟเวอร์หยุด)
python -u app.py

echo.
echo เซิร์ฟเวอร์ปิดแล้ว
pause
