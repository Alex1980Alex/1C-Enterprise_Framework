@echo off
REM View logs from all services

echo ========================================
echo Viewing Logs - Press Ctrl+C to stop
echo ========================================
echo.

cd /d %~dp0\..\docker

if "%1"=="" (
    echo Showing logs from all services...
    docker-compose logs -f --tail=100
) else (
    echo Showing logs from %1...
    docker-compose logs -f --tail=100 %1
)
