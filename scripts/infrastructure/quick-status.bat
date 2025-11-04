@echo off
REM ==============================================================================
REM AI Memory System - Quick Status Check
REM Быстрая проверка статуса без подробностей
REM ==============================================================================

echo Checking services...

REM Docker
docker ps --filter "name=qdrant" --filter "name=neo4j" --filter "name=timescale" --format "{{.Names}}: {{.Status}}" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Docker: NOT RUNNING
) else (
    echo Docker: OK
)

REM Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Ollama: OK
) else (
    echo Ollama: NOT RESPONDING
)

REM Memory AI MCP
claude mcp list 2>nul | findstr /C:"memory-ai" | findstr /C:"Connected" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Memory AI MCP: CONNECTED
) else (
    echo Memory AI MCP: UNKNOWN
)
