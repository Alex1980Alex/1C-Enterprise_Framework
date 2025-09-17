@echo off
cd /d "%~dp0\serena"
.venv\Scripts\python.exe -u -m serena.cli start_mcp_server