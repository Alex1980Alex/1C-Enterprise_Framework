@echo off
REM ==============================================================================
REM AI Memory System - Docker Services Startup
REM Автоматический запуск Docker контейнеров для AI Memory System
REM ==============================================================================

setlocal EnableDelayedExpansion

echo [INFO] Starting AI Memory System Docker Services...
echo.

REM Проверка Docker Desktop
echo [1/6] Checking Docker Desktop...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Docker Desktop not found or not running
    echo [INFO] Attempting to start Docker Desktop...

    REM Попытка запустить Docker Desktop
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        echo [INFO] Docker Desktop starting... Waiting 30 seconds...
        timeout /t 30 /nobreak >nul
    ) else (
        echo [ERROR] Docker Desktop executable not found
        echo [ERROR] Please install Docker Desktop from https://www.docker.com/products/docker-desktop/
        exit /b 1
    )
)

REM Проверка готовности Docker
echo [2/6] Waiting for Docker to be ready...
set RETRY=0
:DOCKER_CHECK
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /a RETRY+=1
    if !RETRY! GEQ 30 (
        echo [ERROR] Docker failed to start after 60 seconds
        exit /b 1
    )
    echo [INFO] Waiting for Docker... (attempt !RETRY!/30)
    timeout /t 2 /nobreak >nul
    goto DOCKER_CHECK
)
echo [OK] Docker is ready!
echo.

REM Переход в директорию с docker-compose
cd /d D:\1C-Enterprise_Framework\ai-memory-system

REM Проверка наличия docker-compose.yml
echo [3/6] Checking docker-compose configuration...
if not exist "docker\docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found in docker\ directory
    exit /b 1
)
echo [OK] docker-compose.yml found
echo.

REM Запуск Docker Compose
echo [4/6] Starting Docker services...
docker-compose -f docker\docker-compose.yml up -d

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start Docker services
    exit /b 1
)
echo [OK] Docker services started
echo.

REM Ожидание инициализации
echo [5/6] Waiting for services to initialize (10 seconds)...
timeout /t 10 /nobreak >nul

REM Проверка статуса контейнеров
echo [6/6] Checking service status...
echo.
docker ps --filter "name=qdrant" --filter "name=neo4j" --filter "name=timescale" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

REM Проверка ключевых сервисов
set ALL_OK=1

docker ps --filter "name=qdrant" --filter "status=running" | findstr /C:"qdrant" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Qdrant is not running
    set ALL_OK=0
) else (
    echo [OK] Qdrant is running
)

docker ps --filter "name=neo4j" --filter "status=running" | findstr /C:"neo4j" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Neo4j is not running
    set ALL_OK=0
) else (
    echo [OK] Neo4j is running
)

docker ps --filter "name=timescale" --filter "status=running" | findstr /C:"timescale" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] TimescaleDB is not running
    set ALL_OK=0
) else (
    echo [OK] TimescaleDB is running
)

echo.
if %ALL_OK%==1 (
    echo [SUCCESS] All Docker services are running!
    exit /b 0
) else (
    echo [WARN] Some services are not running. Check logs with: docker-compose logs
    exit /b 0
)
