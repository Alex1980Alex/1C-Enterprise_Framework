@echo off
setlocal

set PYTHONPATH=D:/1C-Enterprise_Framework/mcp-docling-server
set PYTHONIOENCODING=utf-8
set DOCLING_CACHE_DIR=D:/1C-Enterprise_Framework/cache/docling
set DOCLING_LOG_LEVEL=INFO

"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" server_enhanced.py --transport stdio

endlocal
