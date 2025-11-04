@echo off
REM Memory AI MCP Server - STDIO mode (for Claude Code)

REM Set encoding to UTF-8
chcp 65001 >nul 2>&1

REM Get the directory of this script
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Set parent directory (ai-memory-system)
for %%I in ("%SCRIPT_DIR%\..") do set "PARENT_DIR=%%~fI"

REM Set environment variables for Python
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%PARENT_DIR%\services

REM Change to mcp directory
cd /d "%SCRIPT_DIR%"

REM Run the MCP server in STDIO mode (no logging redirection)
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" "%SCRIPT_DIR%\memory_server.py"
