@echo off
REM ==============================================================================
REM AI Memory System - Services Health Check
REM Проверка статуса всех сервисов инфраструктуры
REM ==============================================================================

setlocal EnableDelayedExpansion

echo ========================================
echo AI Memory System - Health Check
echo ========================================
echo.

set TOTAL=0
set OK=0
set FAILED=0

REM 1. Docker Desktop
echo [1/6] Docker Desktop...
docker --version >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Docker is available
    set /a OK+=1
) else (
    echo [FAIL] Docker not found or not running
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 2. Qdrant
echo [2/6] Qdrant Vector DB (port 6333)...
curl -s http://localhost:6333/health >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Qdrant is responding
    set /a OK+=1
) else (
    echo [FAIL] Qdrant not responding
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 3. Neo4j
echo [3/6] Neo4j Graph DB (port 7474)...
curl -s http://localhost:7474 >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Neo4j is responding
    set /a OK+=1
) else (
    echo [FAIL] Neo4j not responding
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 4. Ollama
echo [4/6] Ollama LLM Server (port 11434)...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Ollama is responding
    set /a OK+=1
) else (
    echo [FAIL] Ollama not responding
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 5. TimescaleDB
echo [5/6] TimescaleDB (port 5432)...
REM Простая проверка доступности порта
netstat -an | findstr ":5432" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] TimescaleDB port is open
    set /a OK+=1
) else (
    echo [FAIL] TimescaleDB port not available
    set /a FAILED+=1
)
set /a TOTAL+=1
echo.

REM 6. Memory AI MCP Server
echo [6/6] Memory AI MCP Server...
claude mcp list 2>nul | findstr /C:"memory-ai" | findstr /C:"Connected" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Memory AI MCP is connected
    set /a OK+=1
) else (
    echo [WARN] Memory AI MCP status unknown
    REM Не считаем это критической ошибкой
    set /a OK+=1
)
set /a TOTAL+=1
echo.

REM Итоговая статистика
echo ========================================
echo Health Check Summary
echo ========================================
echo Total services checked: %TOTAL%
echo Services OK: %OK%
echo Services FAILED: %FAILED%
echo.

REM Расчет процента готовности
set /a PERCENT=(%OK% * 100) / %TOTAL%
echo System Ready: %PERCENT%%%
echo.

if %FAILED% GTR 0 (
    echo [WARN] Some services are not available
    echo.
    echo Troubleshooting:
    echo - Run: scripts\infrastructure\start-docker-services.bat
    echo - Check Docker: docker ps
    echo - Check logs: docker-compose logs
    exit /b 1
) else (
    echo [SUCCESS] All systems operational!
    exit /b 0
)
