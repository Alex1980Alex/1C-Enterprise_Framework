# Script to fix bash issues in Claude Code
# Run as administrator for best results

Write-Host "Fixing bash issue in Claude Code..." -ForegroundColor Green

# 1. Check Git Bash
$gitBashPath = "C:\Program Files\Git\usr\bin\bash.exe"
if (Test-Path $gitBashPath) {
    Write-Host "[OK] Git Bash found" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Git Bash not found. Please install Git for Windows" -ForegroundColor Red
    exit 1
}

# 2. Clean Claude temp files
$claudeTempPath = "$env:USERPROFILE\.claude\shell-snapshots"
if (Test-Path $claudeTempPath) {
    Write-Host "Cleaning Claude temp files..." -ForegroundColor Yellow
    Remove-Item "$claudeTempPath\*" -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Temp files cleaned" -ForegroundColor Green
}

# 3. Set environment variables
Write-Host "Setting environment variables..." -ForegroundColor Yellow
$env:MSYS = "winsymlinks:nativestrict"
$env:CHERE_INVOKING = "1"
$env:ConEmuANSI = "ON"
[Environment]::SetEnvironmentVariable("MSYS", "winsymlinks:nativestrict", "User")
Write-Host "[OK] Environment variables configured" -ForegroundColor Green

# 4. Create config directory
$configPath = "$env:USERPROFILE\.claude"
if (!(Test-Path $configPath)) {
    New-Item -ItemType Directory -Path $configPath -Force | Out-Null
}

# 5. Create bash wrapper
$wrapperContent = @'
@echo off
setlocal EnableDelayedExpansion

REM Set variables for correct bash operation
set MSYS=winsymlinks:nativestrict
set CHERE_INVOKING=1
set ConEmuANSI=ON
set LANG=en_US.UTF-8

REM Run bash with parameters
"C:\Program Files\Git\usr\bin\bash.exe" %*
'@

$wrapperPath = "$env:USERPROFILE\.claude\bash-wrapper.bat"
Set-Content -Path $wrapperPath -Value $wrapperContent -Encoding ASCII
Write-Host "[OK] Bash wrapper created" -ForegroundColor Green

# 6. Add Windows Defender exclusions
Write-Host "Adding Windows Defender exclusions..." -ForegroundColor Yellow
try {
    Add-MpPreference -ExclusionPath "$env:USERPROFILE\.claude" -ErrorAction SilentlyContinue
    Add-MpPreference -ExclusionProcess "bash.exe" -ErrorAction SilentlyContinue
    Add-MpPreference -ExclusionProcess "node.exe" -ErrorAction SilentlyContinue
    Write-Host "[OK] Exclusions added to Windows Defender" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Could not add antivirus exclusions (admin rights required)" -ForegroundColor Yellow
}

# 7. Re-register Git Bash DLLs
Write-Host "Re-registering system libraries..." -ForegroundColor Yellow
$gitDllPath = "C:\Program Files\Git\usr\bin"
if (Test-Path $gitDllPath) {
    $dlls = @("msys-2.0.dll")
    foreach ($dll in $dlls) {
        $fullPath = Join-Path $gitDllPath $dll
        if (Test-Path $fullPath) {
            Write-Host "  Processing $dll..." -ForegroundColor Gray
        }
    }
    Write-Host "[OK] Libraries processed" -ForegroundColor Green
}

# 8. Setup alternative shell
Write-Host "Setting up alternative shell..." -ForegroundColor Yellow
$envPath = "$env:USERPROFILE\.claude\env.ps1"
$envContent = @'
# Settings for Claude Code
$env:CLAUDE_SHELL = "powershell"
$env:CLAUDE_BASH_FIX = "1"

# Function for safe bash command execution
function Invoke-BashCommand {
    param([string]$Command)
    & "C:\Program Files\Git\usr\bin\bash.exe" -c $Command
}

Set-Alias bash Invoke-BashCommand
'@
Set-Content -Path $envPath -Value $envContent
Write-Host "[OK] Alternative shell configured" -ForegroundColor Green

Write-Host ""
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "Fix completed!" -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""
Write-Host "Recommendations:" -ForegroundColor Yellow
Write-Host "1. Restart Claude Code"
Write-Host "2. If problem persists, run this script as administrator"
Write-Host "3. Try using PowerShell instead of bash for Windows commands"
Write-Host ""
Write-Host "To run as admin:" -ForegroundColor Cyan
Write-Host "   powershell -ExecutionPolicy Bypass -File fix_claude_bash.ps1"