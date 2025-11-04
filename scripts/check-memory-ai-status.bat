@echo off
REM Quick status check for Memory-AI MCP Server components
echo ========================================
echo Memory-AI MCP Server Status Check
echo ========================================
echo.

REM Check Docker containers
echo [1/5] Checking Docker containers...
docker ps --filter "name=1c-timescaledb" --filter "name=1c-qdrant" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

REM Check TimescaleDB connection
echo [2/5] Checking TimescaleDB database...
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "SELECT 'DB Connected' as status, COUNT(*) as conversations FROM conversations;" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Cannot connect to TimescaleDB
) else (
    echo OK: TimescaleDB connected
)
echo.

REM Check Qdrant
echo [3/5] Checking Qdrant vector database...
curl -s http://localhost:6333/healthz 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Qdrant not responding
) else (
    echo OK: Qdrant is healthy
)
echo.

REM Check Qdrant collections
echo [4/5] Checking Qdrant collections...
curl -s http://localhost:6333/collections 2>nul | findstr "conversation_memory"
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: conversation_memory collection not found
) else (
    echo OK: conversation_memory collection exists
)
echo.

REM Check MCP server log
echo [5/5] Checking MCP server log...
if exist "D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log" (
    echo Last 5 lines of memory-ai-mcp.log:
    powershell -Command "Get-Content 'D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log' -Tail 5"
) else (
    echo WARNING: Log file not found - MCP server may not have started yet
)
echo.

echo ========================================
echo Status check complete
echo ========================================
echo.
echo To activate Memory-AI in Claude Desktop:
echo 1. Close Claude Desktop completely (check Task Manager)
echo 2. Restart Claude Desktop
echo 3. Test: start_memory_session with project "1C-Enterprise_Framework"
echo.
pause
