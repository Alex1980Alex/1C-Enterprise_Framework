@echo off
REM Test Memory AI MCP Server Initialization
REM This script tests if the server can start and initialize properly

echo ================================================
echo Memory AI MCP Server - Initialization Test
echo ================================================
echo.

REM Set encoding to UTF-8
chcp 65001 >nul 2>&1

REM Set environment variables
set PYTHONIOENCODING=utf-8
set MCP_TIMEOUT=60000
set MCP_MAX_RETRIES=3
set MCP_DEBUG=true

REM Get the directory of this script
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Set parent directory (ai-memory-system)
for %%I in ("%SCRIPT_DIR%\..") do set "PARENT_DIR=%%~fI"

REM Add services to Python path
set PYTHONPATH=%PARENT_DIR%\services;%PYTHONPATH%

echo Test 1: Checking Python installation...
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo ✓ Python found
echo.

echo Test 2: Checking required modules...
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -c "import psycopg2; print('✓ psycopg2')"
if %ERRORLEVEL% neq 0 (
    echo ERROR: psycopg2 not installed
    echo Install with: pip install psycopg2-binary
    pause
    exit /b 1
)

"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -c "import mcp; print('✓ mcp')"
if %ERRORLEVEL% neq 0 (
    echo ERROR: mcp not installed
    echo Install with: pip install mcp
    pause
    exit /b 1
)

"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -c "from qdrant_client import QdrantClient; print('✓ qdrant_client')"
if %ERRORLEVEL% neq 0 (
    echo ERROR: qdrant_client not installed
    echo Install with: pip install qdrant-client
    pause
    exit /b 1
)
echo.

echo Test 3: Checking services import...
cd /d "%SCRIPT_DIR%"
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -c "import sys; sys.path.insert(0, r'%PARENT_DIR%\services'); from conversation_storage import ConversationStorage; from message_vectorization import MessageVectorization; from context_restoration import ContextRestoration; print('✓ All services imported successfully')"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to import services
    pause
    exit /b 1
)
echo.

echo Test 4: Checking PostgreSQL connection...
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='ai_memory', user='ai_user', password='ai_memory_secure_2025'); print('✓ PostgreSQL connected'); conn.close()"
if %ERRORLEVEL% neq 0 (
    echo WARNING: PostgreSQL connection failed
    echo Make sure PostgreSQL/TimescaleDB is running on localhost:5432
    echo Database: ai_memory, User: ai_user
)
echo.

echo Test 5: Checking Qdrant connection...
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -c "from qdrant_client import QdrantClient; client = QdrantClient(host='localhost', port=6333); print('✓ Qdrant connected')"
if %ERRORLEVEL% neq 0 (
    echo WARNING: Qdrant connection failed
    echo Make sure Qdrant is running on localhost:6333
)
echo.

echo ================================================
echo All initialization tests completed!
echo ================================================
echo.
echo To start the MCP server, run:
echo   start-memory-ai-server.bat
echo.
echo Check logs at:
echo   D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log
echo.

pause
