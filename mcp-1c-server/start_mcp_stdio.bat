@echo off
setlocal

REM Настройка путей
set PYTHONPATH=D:/1C-Enterprise_Framework/mcp-1c-integration/src
set PYTHONIOENCODING=utf-8

REM Настройка подключения к 1С
set MCP_ONEC_URL=http://localhost/251017_GKSTCPLK-1794
set MCP_ONEC_USERNAME=a.terletskiy@sodrugestvo.ru
set MCP_ONEC_PASSWORD=1234
set MCP_ONEC_SERVICE_ROOT=mcp
set MCP_LOG_LEVEL=INFO

REM Запуск сервера через модуль py_server
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -m py_server stdio

endlocal
