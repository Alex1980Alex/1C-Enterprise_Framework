@echo off
REM ==============================================================================
REM AI Memory System - Docker Services Shutdown
REM Корректная остановка Docker контейнеров
REM ==============================================================================

setlocal EnableDelayedExpansion

echo [INFO] Stopping AI Memory System Docker Services...
echo.

REM Проверка Docker
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker not found or not running
    exit /b 1
)

REM Переход в директорию с docker-compose
cd /d D:\1C-Enterprise_Framework\ai-memory-system

REM Остановка контейнеров
echo [1/2] Stopping Docker services...
docker-compose -f docker\docker-compose.yml stop

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to stop Docker services
    exit /b 1
)

echo [OK] Docker services stopped
echo.

REM Опциональное удаление контейнеров (раскомментируйте если нужно)
REM echo [2/2] Removing containers...
REM docker-compose -f docker\docker-compose.yml down

echo [SUCCESS] Docker services shutdown complete
echo.
echo To start services again, run: scripts\infrastructure\start-docker-services.bat
