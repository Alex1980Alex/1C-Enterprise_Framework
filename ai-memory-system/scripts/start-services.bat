@echo off
REM Start all AI Memory System services

echo ========================================
echo Starting 1C AI Memory System Services
echo ========================================
echo.

cd /d %~dp0\..\docker

REM Check if .env file exists
if not exist "..\\.env" (
    echo ERROR: .env file not found!
    echo Please create .env file in ai-memory-system directory
    pause
    exit /b 1
)

REM Load environment variables
for /f "delims== tokens=1,2" %%G in (..\.env) do set %%G=%%H

echo Starting Docker Compose services...
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo Checking service health...
docker-compose ps

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo Qdrant Dashboard: http://localhost:6333/dashboard
echo Neo4j Browser:    http://localhost:7474
echo Prometheus:       http://localhost:9090
echo Grafana:          http://localhost:3000
echo.
echo Default Grafana credentials:
echo   Username: admin
echo   Password: %GRAFANA_PASSWORD%
echo.
echo ========================================

pause
