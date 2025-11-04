# PowerShell script to automatically update Claude Desktop config
# Updates memory-ai timeout to 60000 and adds logging

$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$backupPath = "$env:APPDATA\Claude\claude_desktop_config.json.backup"

Write-Host "=== Claude Desktop Config Auto-Update ===" -ForegroundColor Cyan
Write-Host ""

# Check if config file exists
if (-not (Test-Path $configPath)) {
    Write-Host "ERROR: Config file not found at $configPath" -ForegroundColor Red
    exit 1
}

Write-Host "1. Creating backup..." -ForegroundColor Yellow
Copy-Item $configPath $backupPath -Force
Write-Host "   Backup created: $backupPath" -ForegroundColor Green

Write-Host ""
Write-Host "2. Reading current config..." -ForegroundColor Yellow
try {
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
} catch {
    Write-Host "   ERROR: Failed to parse JSON config" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Red
    exit 1
}

Write-Host "   Config loaded successfully" -ForegroundColor Green

Write-Host ""
Write-Host "3. Updating memory-ai section..." -ForegroundColor Yellow

if (-not $config.mcpServers) {
    Write-Host "   ERROR: mcpServers section not found" -ForegroundColor Red
    exit 1
}

if (-not $config.mcpServers.'memory-ai') {
    Write-Host "   WARNING: memory-ai server not found in config" -ForegroundColor Yellow
    Write-Host "   Creating new memory-ai configuration..." -ForegroundColor Yellow
}

# Update memory-ai configuration
$config.mcpServers.'memory-ai' = [PSCustomObject]@{
    command = "D:/1C-Enterprise_Framework/ai-memory-system/mcp/start-memory-ai-server.bat"
    args = @()
    cwd = "D:/1C-Enterprise_Framework/ai-memory-system/mcp"
    env = [PSCustomObject]@{
        PYTHONIOENCODING = "utf-8"
        MCP_TIMEOUT = "60000"
        MCP_MAX_RETRIES = "3"
        MCP_DEBUG = "true"
        MCP_LOG_FILE = "D:/1C-Enterprise_Framework/cache/memory-ai-mcp.log"
    }
    timeout = 60000
}

Write-Host "   Updated timeout: 30000 -> 60000" -ForegroundColor Green
Write-Host "   Added MCP_DEBUG: true" -ForegroundColor Green
Write-Host "   Added MCP_LOG_FILE" -ForegroundColor Green

Write-Host ""
Write-Host "4. Saving updated config..." -ForegroundColor Yellow

try {
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Host "   Config saved successfully" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Failed to save config" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Restoring backup..." -ForegroundColor Yellow
    Copy-Item $backupPath $configPath -Force
    exit 1
}

Write-Host ""
Write-Host "=== Update Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Changes made:" -ForegroundColor Yellow
Write-Host "  - Timeout: 30000 -> 60000 ms (60 seconds)" -ForegroundColor White
Write-Host "  - Added debug logging" -ForegroundColor White
Write-Host "  - Log file: D:/1C-Enterprise_Framework/cache/memory-ai-mcp.log" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Restart Claude Desktop to apply changes" -ForegroundColor White
Write-Host "  2. Test memory-ai server connection" -ForegroundColor White
Write-Host "  3. Check logs at:" -ForegroundColor White
Write-Host "     D:/1C-Enterprise_Framework/cache/memory-ai-mcp.log" -ForegroundColor Gray
Write-Host ""
Write-Host "Backup saved at:" -ForegroundColor Yellow
Write-Host "  $backupPath" -ForegroundColor Gray
Write-Host ""

# Ask if user wants to open the config in editor
$openEditor = Read-Host "Open config in editor to verify? (y/n)"
if ($openEditor -eq 'y' -or $openEditor -eq 'Y') {
    notepad $configPath
}
