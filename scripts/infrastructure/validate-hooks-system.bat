@echo off
REM ==============================================================================
REM AI Memory System - Hooks System Validation
REM Полная проверка системы перед запуском
REM ==============================================================================

setlocal EnableDelayedExpansion

echo ========================================
echo AI Memory System - Hooks Validation
echo ========================================
echo.

set TOTAL_CHECKS=0
set PASSED=0
set FAILED=0
set WARNINGS=0

REM ============================================================
REM 1. Проверка структуры файлов
REM ============================================================
echo [1/7] Checking file structure...
echo.

set FILES_OK=1

REM Хук
if exist ".claude\hooks\pre-prompt.hook.sh" (
    echo [OK] .claude\hooks\pre-prompt.hook.sh
    set /a PASSED+=1
) else (
    echo [FAIL] .claude\hooks\pre-prompt.hook.sh NOT FOUND
    set FILES_OK=0
    set /a FAILED+=1
)
set /a TOTAL_CHECKS+=1

REM Документация хуков
if exist ".claude\hooks\README.md" (
    echo [OK] .claude\hooks\README.md
    set /a PASSED+=1
) else (
    echo [WARN] .claude\hooks\README.md NOT FOUND
    set /a WARNINGS+=1
)
set /a TOTAL_CHECKS+=1

if exist ".claude\hooks\ACTIVATION_GUIDE.md" (
    echo [OK] .claude\hooks\ACTIVATION_GUIDE.md
    set /a PASSED+=1
) else (
    echo [WARN] .claude\hooks\ACTIVATION_GUIDE.md NOT FOUND
    set /a WARNINGS+=1
)
set /a TOTAL_CHECKS+=1

REM Скрипты инфраструктуры
if exist "scripts\infrastructure\start-docker-services.bat" (
    echo [OK] scripts\infrastructure\start-docker-services.bat
    set /a PASSED+=1
) else (
    echo [FAIL] scripts\infrastructure\start-docker-services.bat NOT FOUND
    set FILES_OK=0
    set /a FAILED+=1
)
set /a TOTAL_CHECKS+=1

if exist "scripts\infrastructure\check-all-services.bat" (
    echo [OK] scripts\infrastructure\check-all-services.bat
    set /a PASSED+=1
) else (
    echo [FAIL] scripts\infrastructure\check-all-services.bat NOT FOUND
    set FILES_OK=0
    set /a FAILED+=1
)
set /a TOTAL_CHECKS+=1

if exist "scripts\infrastructure\stop-docker-services.bat" (
    echo [OK] scripts\infrastructure\stop-docker-services.bat
    set /a PASSED+=1
) else (
    echo [WARN] scripts\infrastructure\stop-docker-services.bat NOT FOUND
    set /a WARNINGS+=1
)
set /a TOTAL_CHECKS+=1

echo.

REM ============================================================
REM 2. Проверка bash
REM ============================================================
echo [2/7] Checking bash availability...
bash --version >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] bash is available
    set /a PASSED+=1
) else (
    echo [FAIL] bash not found - Git for Windows required
    set /a FAILED+=1
)
set /a TOTAL_CHECKS+=1
echo.

REM ============================================================
REM 3. Проверка синтаксиса bash хука
REM ============================================================
echo [3/7] Validating bash syntax...
bash -n .claude\hooks\pre-prompt.hook.sh >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Bash syntax is valid
    set /a PASSED+=1
) else (
    echo [FAIL] Bash syntax errors detected
    bash -n .claude\hooks\pre-prompt.hook.sh
    set /a FAILED+=1
)
set /a TOTAL_CHECKS+=1
echo.

REM ============================================================
REM 4. Проверка прав на выполнение (только для Linux/Mac)
REM ============================================================
echo [4/7] Checking execute permissions...
REM На Windows не критично, пропускаем
echo [SKIP] Execute permissions (Windows)
echo.

REM ============================================================
REM 5. Проверка docker-compose.yml
REM ============================================================
echo [5/7] Checking docker-compose configuration...
if exist "ai-memory-system\docker\docker-compose.yml" (
    echo [OK] docker-compose.yml found
    set /a PASSED+=1
) else (
    echo [WARN] docker-compose.yml not found
    echo       Location: ai-memory-system\docker\docker-compose.yml
    set /a WARNINGS+=1
)
set /a TOTAL_CHECKS+=1
echo.

REM ============================================================
REM 6. Проверка Docker Desktop
REM ============================================================
echo [6/7] Checking Docker Desktop...
docker --version >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Docker is available
    docker --version
    set /a PASSED+=1
) else (
    echo [WARN] Docker not found or not running
    echo       This will be handled by hooks automatically
    set /a WARNINGS+=1
)
set /a TOTAL_CHECKS+=1
echo.

REM ============================================================
REM 7. Проверка Claude CLI
REM ============================================================
echo [7/7] Checking Claude CLI...
claude --version >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Claude CLI is available
    set /a PASSED+=1
) else (
    echo [WARN] Claude CLI not found in PATH
    echo       Make sure you're running inside Claude Code
    set /a WARNINGS+=1
)
set /a TOTAL_CHECKS+=1
echo.

REM ============================================================
REM Итоговый отчет
REM ============================================================
echo ========================================
echo Validation Summary
echo ========================================
echo Total checks: %TOTAL_CHECKS%
echo Passed: %PASSED%
echo Failed: %FAILED%
echo Warnings: %WARNINGS%
echo.

set /a SUCCESS_RATE=(%PASSED% * 100) / %TOTAL_CHECKS%
echo Success Rate: %SUCCESS_RATE%%%
echo.

REM ============================================================
REM Рекомендации
REM ============================================================
if %FAILED% GTR 0 (
    echo [ERROR] Critical issues found!
    echo.
    echo Please fix the following:
    if %FILES_OK%==0 (
        echo - Missing required files
    )
    echo.
    echo After fixing issues, run this script again:
    echo   scripts\infrastructure\validate-hooks-system.bat
    echo.
    exit /b 1
)

if %WARNINGS% GTR 0 (
    echo [WARNING] Some optional components missing
    echo.
    echo The system will work but some features may be limited:
    echo - Docker: Will be started automatically by hooks
    echo - Documentation: Helpful but not required
    echo.
)

if %FAILED%==0 (
    echo ========================================
    echo [SUCCESS] System is ready!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Restart Claude Code:
    echo    exit
    echo    claude
    echo.
    echo 2. Write your first prompt
    echo.
    echo 3. The hook will automatically check infrastructure
    echo.
    echo ========================================
    echo.
    exit /b 0
)
