# AI Memory MCP Server - Quick Start Guide

## Status: Configuration Added ✓

AI Memory MCP Server has been successfully added to Claude Code configuration.

## Next Steps (3 Easy Steps)

### Step 1: Find Neo4j Password

Open Neo4j Browser: http://localhost:7474

Try these passwords:
- `neo4j` (default)
- `password`
- `admin`

When you find the working password, **write it down!**

### Step 2: Update Password

Edit file: `%APPDATA%\Claude\claude_desktop_config.json`

Find this line:
```json
"NEO4J_PASSWORD": "your_password"
```

Replace `your_password` with your actual Neo4j password.

Save the file.

### Step 3: Restart Claude Code

1. Close ALL Claude Code windows
2. Wait 5 seconds
3. Start Claude Code

## Verify It Works

In Claude Code, try this:
```
Use the search_bsl_code tool to search for "Справочники"
```

If the tool runs successfully - you're done! 🎉

## Troubleshooting

### Can't find Neo4j password?

Run this script:
```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
python test_neo4j_password.py
```

Or see detailed guide: `CHECK_NEO4J_PASSWORD.md`

### MCP Server not appearing?

1. Check config file location: `%APPDATA%\Claude\claude_desktop_config.json`
2. Verify JSON syntax is valid
3. Restart Claude Code completely
4. Check Claude Code logs

### Need more help?

See complete documentation:
- `D:\Проекты\MCP_SETUP_COMPLETED.md` - Complete setup guide
- `MCP_SERVER_SETUP.md` - Detailed setup instructions
- `CHECK_NEO4J_PASSWORD.md` - Password checking guide

## Available Tools

Once configured, you have access to:

1. **search_bsl_code** - Semantic search through BSL code
2. **intelligent_search** - Multi-dimensional intelligent search
3. **analyze_graph** - Code dependency analysis
4. **get_search_history** - View search history
5. **clear_cache** - Clear caches

## Test MCP Server Standalone

Before using in Claude Code:
```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
python mcp_server\server_fastmcp.py
```

Press Ctrl+C to stop.

## Configuration Location

Your configuration is stored in:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Full path usually:
```
C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json
```

## That's It!

Three simple steps:
1. ✓ Find password
2. ✓ Update config
3. ✓ Restart Claude Code

Happy coding! 🚀
