@echo off
REM Startup script for AI Memory MCP Server
REM Location: D:\1C-Enterprise_Framework\ai-memory-system\mcp_server\start_mcp_server.bat

echo ====================================
echo AI Memory MCP Server Startup
echo ====================================
echo.

REM Set Python path
set PYTHONPATH=D:\1C-Enterprise_Framework\ai-memory-system

REM Change to project directory
cd /d D:\1C-Enterprise_Framework\ai-memory-system

REM Start MCP server
echo Starting MCP Server (FastMCP)...
echo.
python mcp_server\server_fastmcp.py

pause
