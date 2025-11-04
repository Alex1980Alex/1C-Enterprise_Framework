@echo off
chcp 65001 >nul
echo ========================================
echo Проверка Memory MCP Services
echo ========================================
echo.

echo [1/4] Проверка Docker контейнеров...
docker ps --format "table {{.Names}}\t{{.Status}}" | findstr /C:"timescale" /C:"qdrant"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker контейнеры не запущены
    echo.
    echo Запустить?
    echo   docker start 1c-timescaledb 1c-qdrant
    goto :ollama_check
)
echo ✅ Docker контейнеры работают
echo.

:ollama_check
echo [2/4] Проверка Ollama...
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ollama не отвечает
    echo.
    echo Запустить вручную:
    echo   "C:\Users\AlexT\AppData\Local\Programs\Ollama\ollama.exe" serve
    goto :model_check
)
echo ✅ Ollama работает
curl -s http://localhost:11434/api/version
echo.

:model_check
echo [3/4] Проверка модели nomic-embed-text...
ollama list | findstr /C:"nomic-embed"
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Модель не установлена
    echo.
    echo Установить:
    echo   ollama pull nomic-embed-text
    goto :qdrant_check
)
echo ✅ Модель установлена
echo.

:qdrant_check
echo [4/4] Проверка Qdrant коллекций...
curl -s http://localhost:6333/collections 2>nul | findstr /C:"conversation_memory"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Коллекция conversation_memory не найдена (создастся автоматически)
    goto :summary
)
echo ✅ Коллекция conversation_memory готова
echo.

:summary
echo ========================================
echo Итоговый статус:
echo ========================================
docker ps --filter "name=1c-timescaledb" --format "TimescaleDB: {{.Status}}"
docker ps --filter "name=1c-qdrant" --format "Qdrant: {{.Status}}"
curl -s http://localhost:11434/api/version | findstr "version" >nul 2>&1 && echo Ollama: Running || echo Ollama: Not running
echo ========================================
echo.
echo Для запуска AI Memory все сервисы должны работать.
echo Official Memory работает всегда (не требует сервисов).
echo.
pause
