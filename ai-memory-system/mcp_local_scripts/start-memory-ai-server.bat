@echo off
REM Memory AI MCP Server startup script

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

REM Set log file path
set MCP_LOG_FILE=D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log

REM Create cache directory if it doesn't exist
if not exist "D:\1C-Enterprise_Framework\cache" mkdir "D:\1C-Enterprise_Framework\cache"

REM Change to mcp directory
cd /d "%SCRIPT_DIR%"

REM Log startup
echo [%DATE% %TIME%] Starting Memory AI MCP Server >> "%MCP_LOG_FILE%"
echo [%DATE% %TIME%] SCRIPT_DIR: %SCRIPT_DIR% >> "%MCP_LOG_FILE%"
echo [%DATE% %TIME%] PARENT_DIR: %PARENT_DIR% >> "%MCP_LOG_FILE%"
echo [%DATE% %TIME%] PYTHONPATH: %PYTHONPATH% >> "%MCP_LOG_FILE%"
echo [%DATE% %TIME%] MCP_TIMEOUT: %MCP_TIMEOUT% >> "%MCP_LOG_FILE%"

REM Run the MCP server with full logging (stdout and stderr)
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" "%SCRIPT_DIR%\memory_server_fixed.py" >> "%MCP_LOG_FILE%" 2>&1

REM Log exit
echo [%DATE% %TIME%] Memory AI MCP Server stopped with error level: %ERRORLEVEL% >> "%MCP_LOG_FILE%"
