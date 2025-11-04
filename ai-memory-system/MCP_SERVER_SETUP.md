# AI Memory MCP Server - Setup Instructions

## Step 1: Configure Neo4j Password ✅

The MCP server now uses environment variables for configuration. You have two options:

### Option A: Using Environment Variables (Recommended)

1. **Set environment variables** before starting the MCP server:

```bash
# Windows (PowerShell)
$env:NEO4J_PASSWORD="your_actual_neo4j_password"

# Windows (CMD)
set NEO4J_PASSWORD=your_actual_neo4j_password

# Linux/Mac
export NEO4J_PASSWORD="your_actual_neo4j_password"
```

2. **Or create a `.env` file** in the `ai-memory-system` directory:

```bash
# Copy the example file
copy .env.example .env

# Edit .env and update NEO4J_PASSWORD
NEO4J_PASSWORD=your_actual_neo4j_password
```

### Option B: Direct Configuration (Simple)

If you don't want to use environment variables, you can directly edit the default value in `server_fastmcp.py:77`:

```python
password=os.getenv("NEO4J_PASSWORD", "your_actual_password_here")
```

## Step 2: Configure Claude Code Integration

Copy the MCP server configuration to Claude Code:

### Windows

```powershell
# Location of Claude Code config
$claudeConfig = "$env:APPDATA\Claude\claude_desktop_config.json"

# Create directory if it doesn't exist
New-Item -ItemType Directory -Force -Path (Split-Path $claudeConfig)

# Copy configuration
Copy-Item "D:\Проекты\MCP_CONFIG_EXAMPLE.json" $claudeConfig
```

### Manual Configuration

1. Open Claude Code configuration file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "ai-memory-system": {
      "command": "python",
      "args": [
        "D:/1C-Enterprise_Framework/ai-memory-system/mcp_server/server_fastmcp.py"
      ],
      "cwd": "D:/1C-Enterprise_Framework/ai-memory-system",
      "env": {
        "PYTHONPATH": "D:/1C-Enterprise_Framework/ai-memory-system",
        "NEO4J_PASSWORD": "your_actual_neo4j_password"
      },
      "description": "AI Memory System for BSL code analysis"
    }
  }
}
```

3. **Update paths** if your installation is in a different location

4. **Restart Claude Code** to load the new configuration

## Step 3: Verify Installation

### Test MCP Server Standalone

```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
python mcp_server\server_fastmcp.py
```

Expected output:
```
INFO:__main__:=== Starting AI Memory MCP Server (FastMCP) ===
```

Press `Ctrl+C` to stop.

### Test Through Claude Code

1. Restart Claude Code
2. In a conversation, check if the MCP server is loaded:
   - Look for "ai-memory-system" in the available tools
3. Try a test command:
   ```
   Use the search_bsl_code tool to search for "Справочники"
   ```

## Available Environment Variables

All configuration can be done via environment variables or `.env` file:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=bsl_code

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:6.7b
```

## Troubleshooting

### MCP Server Not Starting

1. **Check Python is in PATH**: `python --version`
2. **Check MCP SDK installed**: `pip show mcp`
3. **Check logs** in Claude Code console

### Neo4j Connection Failed

1. **Verify Neo4j is running**: Check `http://localhost:7474`
2. **Check password**: Try logging in via Neo4j Browser
3. **Update environment variable** with correct password

### Claude Code Not Detecting MCP Server

1. **Verify config file exists** in the correct location
2. **Check JSON syntax** is valid (use https://jsonlint.com)
3. **Restart Claude Code** completely (quit and reopen)
4. **Check Claude Code logs** for error messages

## Next Steps

Once configured, you can use these MCP tools in Claude Code:

1. **search_bsl_code** - Semantic search through BSL code
2. **intelligent_search** - Multi-dimensional intelligent search
3. **analyze_graph** - Analyze code dependencies (requires Neo4j)
4. **get_search_history** - View recent searches
5. **clear_cache** - Clear search history

For detailed usage, see: `D:\Проекты\MCP_SERVER_COMPLETE_2025-11-04.md`
