@echo off
REM Stop all AI Memory System services

echo ========================================
echo Stopping 1C AI Memory System Services
echo ========================================
echo.

cd /d %~dp0\..\docker

echo Stopping Docker Compose services...
docker-compose stop

echo.
echo ========================================
echo Services Stopped!
echo ========================================
echo.
echo To completely remove containers and volumes, run:
echo   docker-compose down -v
echo.

pause
