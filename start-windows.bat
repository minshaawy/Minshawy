@echo off
chcp 65001 >nul
title Minshawi Tribute - Server
cd /d "%~dp0"

echo.
echo ============================================
echo    موقع الشيخ المنشاوي - Minshawi Tribute
echo              يبدأ التشغيل...
echo ============================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [X] Python غير مثبت / Python is not installed
        echo.
        echo حمّل Python من / Download Python from:
        echo https://www.python.org/downloads/
        echo.
        echo IMPORTANT: During install check "Add Python to PATH"
        echo.
        pause
        exit /b 1
    ) else (
        set PY_CMD=py
    )
) else (
    set PY_CMD=python
)

set PORT=8000
set URL=http://localhost:%PORT%

echo [V] الخادم شغال على / Server running at:
echo    %URL%
echo.
echo [+] افتح المتصفح على هذا العنوان
echo [+] Browser will open automatically
echo.
echo [!] لإيقاف الخادم: اضغط Ctrl+C ثم Y
echo [!] To stop: press Ctrl+C then Y
echo.

REM Open browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start %URL%"

REM Start server
%PY_CMD% -m http.server %PORT%

pause
