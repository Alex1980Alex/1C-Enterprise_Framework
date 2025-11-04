@echo off
REM Post Tool Result Auto-Save Hook (Windows version)
REM Автоматическое сохранение важной информации в Memory MCP после операций
REM
REM ВАЖНО: Хук получает JSON через stdin согласно документации Claude Code
REM JSON содержит: tool_name, tool_input, tool_response, session_id, cwd

REM Путь к скриптам
set "SCRIPT_DIR=%~dp0"
set "AUTO_SAVE_SCRIPT=%SCRIPT_DIR%auto-save.py"
set "CONFIG_FILE=%SCRIPT_DIR%config.json"

REM Проверка конфигурации
if not exist "%CONFIG_FILE%" exit /b 0

REM Чтение настройки enabled из config.json
findstr /C:"\"enabled\": true" "%CONFIG_FILE%" >nul 2>&1
if errorlevel 1 (
    REM Автосохранение отключено - это нормально
    exit /b 0
)

REM Запуск Python скрипта с передачей stdin
REM Python скрипт сам читает hook JSON из stdin и обрабатывает его
if exist "%AUTO_SAVE_SCRIPT%" (
    python "%AUTO_SAVE_SCRIPT%"
    REM Игнорируем код возврата - хук не должен блокировать работу
    exit /b 0
)

exit /b 0
