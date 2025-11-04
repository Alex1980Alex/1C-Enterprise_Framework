@echo off
REM ==============================================================================
REM AI Memory System - Docker Services Restart
REM Перезапуск всех Docker контейнеров
REM ==============================================================================

echo [INFO] Restarting AI Memory System Docker Services...
echo.

REM Остановка
call "%~dp0stop-docker-services.bat"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to stop services
    exit /b 1
)

echo.
echo [INFO] Waiting 5 seconds before restart...
timeout /t 5 /nobreak >nul

REM Запуск
call "%~dp0start-docker-services.bat"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start services
    exit /b 1
)

echo.
echo [SUCCESS] Services restarted successfully!
