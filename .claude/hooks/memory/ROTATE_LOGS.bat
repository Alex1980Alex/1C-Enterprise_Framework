@echo off
REM Log Rotation - Ротация логов hooks
REM Использование:
REM   ROTATE_LOGS.bat        - Выполнить ротацию
REM   ROTATE_LOGS.bat status - Показать статус логов

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo ========================================
echo   LOG ROTATION
echo ========================================
echo.

if "%1"=="status" (
    python log-rotation.py status
) else (
    python log-rotation.py
)

echo.
pause
