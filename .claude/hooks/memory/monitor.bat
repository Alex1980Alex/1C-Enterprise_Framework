@echo off
REM Hooks Monitoring Dashboard
REM Запуск дашборда мониторинга хуков

cd /d "%~dp0"
python monitor.py
pause
