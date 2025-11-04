@echo off
REM Post User Prompt Analysis Hook
REM Анализ новой задачи от пользователя через stdin (JSON)
REM ВАЖНО: Hook получает данные через stdin, НЕ через переменные окружения

set "SCRIPT_DIR=%~dp0"
set "ANALYSIS_SCRIPT=%SCRIPT_DIR%task-analysis.py"
set "CONFIG_FILE=%SCRIPT_DIR%config.json"

REM Проверка конфигурации
if not exist "%CONFIG_FILE%" (
    REM Нет конфига - потребляем stdin и выходим
    more >nul 2>&1
    exit /b 0
)

REM Проверка enabled
findstr /C:"\"enabled\": true" "%CONFIG_FILE%" >nul 2>&1
if errorlevel 1 (
    REM Отключено - потребляем stdin и выходим
    more >nul 2>&1
    exit /b 0
)

REM Запускаем Python скрипт с передачей stdin
if exist "%ANALYSIS_SCRIPT%" (
    python "%ANALYSIS_SCRIPT%"
) else (
    REM Скрипт не найден - потребляем stdin и выходим
    more >nul 2>&1
)

REM ВСЕГДА возвращаем успех
exit /b 0
