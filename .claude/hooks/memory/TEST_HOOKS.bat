@echo off
REM Тестовый скрипт для проверки всех hooks
REM Запустите ПОСЛЕ перезапуска Claude Code

echo.
echo ========================================
echo   ТЕСТИРОВАНИЕ HOOKS
echo ========================================
echo.

echo [1/3] Тестирование pre-prompt-check.bat...
call "%~dp0pre-prompt-check.bat"
if errorlevel 1 (
    echo [FAIL] pre-prompt-check.bat вернул ошибку
    pause
    exit /b 1
) else (
    echo [OK] pre-prompt-check.bat завершился успешно
)
echo.

echo [2/3] Тестирование post-user-prompt-analysis.bat...
set "CLAUDE_USER_PROMPT=Тестовая задача для проверки hooks"
set "CLAUDE_SESSION_ID=test-12345"
call "%~dp0post-user-prompt-analysis.bat"
if errorlevel 1 (
    echo [FAIL] post-user-prompt-analysis.bat вернул ошибку
    pause
    exit /b 1
) else (
    echo [OK] post-user-prompt-analysis.bat завершился успешно
)
echo.

echo [3/3] Тестирование post-tool-save.bat...
call "%~dp0post-tool-save.bat"
if errorlevel 1 (
    echo [FAIL] post-tool-save.bat вернул ошибку
    pause
    exit /b 1
) else (
    echo [OK] post-tool-save.bat завершился успешно
)
echo.

echo ========================================
echo   ВСЕ ТЕСТЫ ПРОЙДЕНЫ!
echo ========================================
echo.
echo Hooks работают корректно.
echo Теперь перезапустите Claude Code для применения изменений.
echo.
pause
