@echo off
REM Pre-Prompt Memory Check Hook
REM Максимально упрощённая версия - просто потребляет stdin и выходит
REM ВАЖНО: Hook НИКОГДА не блокирует работу Claude Code

REM Потребляем stdin через findstr (более надежно чем more)
REM findstr всегда читает весь stdin до EOF
findstr ".*" >nul 2>&1

REM ВСЕГДА возвращаем успех (0)
exit /b 0
