@echo off
echo Starting Serena MCP Server for 1C-Enterprise Framework...
cd /d "%~dp0serena"

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv is not installed or not in PATH
    echo Please install uv: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    uv venv
)

REM Install dependencies if needed
if not exist ".venv\pyvenv.cfg" (
    echo Installing dependencies...
    uv sync
)

echo Starting Serena MCP Server...
uv run serena-mcp-server --project "1C-Enterprise_Framework"

pause