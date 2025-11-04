@echo off
REM Automatic installation script for Docker Desktop and Ollama
REM Run this after download completes

echo ========================================
echo Docker Desktop and Ollama Installer
echo ========================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with administrator privileges
) else (
    echo [ERROR] This script requires administrator privileges
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Step 1: Checking Docker Desktop installer...
echo ========================================

set DOCKER_INSTALLER=%TEMP%\DockerDesktopInstaller.exe

if exist "%DOCKER_INSTALLER%" (
    echo [OK] Docker Desktop installer found
    echo Path: %DOCKER_INSTALLER%

    REM Get file size
    for %%A in ("%DOCKER_INSTALLER%") do set DOCKER_SIZE=%%~zA
    echo Size: %DOCKER_SIZE% bytes

    REM Check if size is reasonable (should be > 500MB = 524288000 bytes)
    if %DOCKER_SIZE% LSS 500000000 (
        echo [WARNING] File size seems too small, download may be incomplete
        echo Expected: ~550MB, Got: %DOCKER_SIZE% bytes
        pause
    )
) else (
    echo [ERROR] Docker Desktop installer not found at: %DOCKER_INSTALLER%
    echo.
    echo Please ensure the download has completed first.
    echo You can download manually from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo.
echo Step 2: Installing Docker Desktop...
echo ========================================
echo This will take 5-10 minutes...
echo.

"%DOCKER_INSTALLER%" install --quiet --accept-license --no-windows-containers

if %errorLevel% == 0 (
    echo [OK] Docker Desktop installed successfully
) else (
    echo [ERROR] Docker Desktop installation failed with error code: %errorLevel%
    echo.
    echo Try manual installation:
    echo 1. Run: %DOCKER_INSTALLER%
    echo 2. Follow on-screen instructions
    pause
    exit /b 1
)

echo.
echo Step 3: Checking Ollama...
echo ========================================

REM Check if Ollama is already installed
where ollama >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Ollama is already installed
    ollama --version
) else (
    echo [INFO] Ollama not found, preparing to install...

    REM Download Ollama installer
    echo Downloading Ollama installer...
    set OLLAMA_INSTALLER=%TEMP%\OllamaSetup.exe

    curl -L "https://ollama.com/download/OllamaSetup.exe" -o "%OLLAMA_INSTALLER%" --progress-bar

    if exist "%OLLAMA_INSTALLER%" (
        echo [OK] Ollama installer downloaded

        echo Installing Ollama...
        "%OLLAMA_INSTALLER%" /S

        if %errorLevel% == 0 (
            echo [OK] Ollama installed successfully
        ) else (
            echo [WARNING] Ollama installation may have issues
            echo You can install manually from: https://ollama.com/download
        )
    ) else (
        echo [ERROR] Failed to download Ollama installer
        echo Please download manually from: https://ollama.com/download
    )
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo IMPORTANT: You MUST restart your computer now!
echo.
echo After restart:
echo 1. Docker Desktop will start automatically
echo 2. Wait for "Docker Desktop is running" in system tray
echo 3. Open new command prompt and verify:
echo    - docker --version
echo    - ollama --version
echo.
echo Then run: scripts\start-services.bat
echo.

set /p RESTART="Restart computer now? (Y/N): "
if /i "%RESTART%"=="Y" (
    echo Restarting in 10 seconds...
    shutdown /r /t 10 /c "Restarting for Docker and Ollama installation"
) else (
    echo.
    echo Please restart manually when ready.
)

pause
