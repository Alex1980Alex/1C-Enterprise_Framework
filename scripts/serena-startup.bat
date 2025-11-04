@echo off
setlocal
set "PATH=D:\1C-Enterprise_Framework\serena\.venv\Scripts;%PATH%"
"D:\1C-Enterprise_Framework\serena\.venv\Scripts\python.exe" -m serena.cli start-mcp-server --context ide-assistant --project "D:/1C-Enterprise_Framework"
