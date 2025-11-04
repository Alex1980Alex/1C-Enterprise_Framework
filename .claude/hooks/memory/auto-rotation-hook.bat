@echo off
REM Auto Log Rotation Hook
REM Автоматическая ротация логов при превышении размера
REM Срабатывает не каждый раз, а периодически (раз в 10 промптов)

set "SCRIPT_DIR=%~dp0"
set "AUTO_ROTATION_SCRIPT=%SCRIPT_DIR%auto-log-rotation.py"

REM Потребляем stdin через findstr и передаем в Python через pipe
REM Python скрипт сам проверяет счетчик и решает нужна ли ротация
if exist "%AUTO_ROTATION_SCRIPT%" (
    findstr ".*" 2>nul | python "%AUTO_ROTATION_SCRIPT%" >nul 2>&1
) else (
    findstr ".*" >nul 2>&1
)

REM ВСЕГДА возвращаем успех
exit /b 0
