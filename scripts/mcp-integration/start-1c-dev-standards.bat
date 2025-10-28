@echo off
REM 1C Development Standards MCP Server Launcher
REM Запускает Python MCP сервер для документации по стандартам разработки 1C

set PYTHONIOENCODING=utf-8
set DOCS_ROOT=D:/1C-Enterprise_Framework/Документация разработчика
set PYTHONPATH=D:/1C-Enterprise_Framework/scripts/docs-mcp

"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" "D:\1C-Enterprise_Framework\scripts\docs-mcp\mcp_server.py"
