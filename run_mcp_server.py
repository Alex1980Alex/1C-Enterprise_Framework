#!/usr/bin/env python3
"""
Working Serena MCP Server
Simplified implementation for Claude Desktop
"""

import sys
import os
import json
import asyncio
import logging
from typing import Any, Dict, List

# Configure logging to stderr only
logging.basicConfig(
    level=logging.ERROR,
    stream=sys.stderr,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
)

# Ensure all print goes to stderr except JSON-RPC
original_print = print
def stderr_print(*args, **kwargs):
    kwargs['file'] = sys.stderr
    original_print(*args, **kwargs)

import builtins
builtins.print = stderr_print

# Note: Serena components are disabled in this simplified setup

try:
    from mcp import types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server

    # Serena components are not available in this setup
    SERENA_AVAILABLE = False
    stderr_print("Serena components disabled (using simplified MCP server)")

    # Create MCP server
    server = Server("serena")

    @server.list_tools()
    async def list_tools() -> List[types.Tool]:
        """List available tools"""
        tools = [
            types.Tool(
                name="read_file",
                description="Read a file from the filesystem",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"}
                    },
                    "required": ["path"]
                }
            ),
            types.Tool(
                name="list_directory",
                description="List contents of a directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path to list"}
                    },
                    "required": ["path"]
                }
            ),
            types.Tool(
                name="search_files",
                description="Search for patterns in files",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Pattern to search for"},
                        "path": {"type": "string", "description": "Path to search in (default: current directory)"},
                        "file_types": {"type": "array", "items": {"type": "string"}, "description": "File extensions to search (e.g., ['.py', '.js'])"}
                    },
                    "required": ["pattern"]
                }
            )
        ]

        if SERENA_AVAILABLE:
            tools.append(
                types.Tool(
                    name="serena_analyze",
                    description="Analyze code using Serena AI capabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Analysis query"},
                            "context": {"type": "string", "description": "Code context or file path"}
                        },
                        "required": ["query"]
                    }
                )
            )

        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle tool calls"""
        try:
            if name == "read_file":
                path = arguments.get("path", "")
                try:
                    if os.path.exists(path):
                        # Check file size to prevent memory issues (limit to 1MB)
                        file_size = os.path.getsize(path)
                        if file_size > 1024 * 1024:  # 1MB limit
                            return [types.TextContent(type="text", text=f"Error: File '{path}' is too large ({file_size} bytes). Maximum size is 1MB.")]

                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        return [types.TextContent(type="text", text=f"File: {path}\n\n{content}")]
                    else:
                        return [types.TextContent(type="text", text=f"Error: File '{path}' not found")]
                except Exception as e:
                    return [types.TextContent(type="text", text=f"Error reading file '{path}': {str(e)}")]

            elif name == "list_directory":
                path = arguments.get("path", ".")
                try:
                    if os.path.isdir(path):
                        items = []
                        for item in sorted(os.listdir(path)):
                            item_path = os.path.join(path, item)
                            if os.path.isdir(item_path):
                                items.append(f"📁 {item}/")
                            else:
                                items.append(f"📄 {item}")
                        content = f"Directory: {path}\n\n" + "\n".join(items)
                        return [types.TextContent(type="text", text=content)]
                    else:
                        return [types.TextContent(type="text", text=f"Error: Directory '{path}' not found")]
                except Exception as e:
                    return [types.TextContent(type="text", text=f"Error listing directory '{path}': {str(e)}")]

            elif name == "search_files":
                pattern = arguments.get("pattern", "")
                path = arguments.get("path", ".")
                file_types = arguments.get("file_types", ['.py', '.js', '.ts', '.bsl', '.txt', '.md', '.cf', '.epf', '.erf', '.cfe', '.xml'])

                try:
                    results = []
                    search_count = 0

                    if os.path.isfile(path):
                        files_to_search = [path]
                    else:
                        files_to_search = []
                        for root, dirs, files in os.walk(path):
                            # Skip hidden directories and common ignore patterns
                            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

                            for file in files:
                                if any(file.endswith(ext) for ext in file_types):
                                    files_to_search.append(os.path.join(root, file))
                                    if len(files_to_search) > 100:  # Limit number of files
                                        break
                            if len(files_to_search) > 100:
                                break

                    for filepath in files_to_search:
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    if pattern.lower() in line.lower():
                                        results.append(f"{filepath}:{line_num}: {line.strip()}")
                                        search_count += 1
                                        if search_count > 50:  # Limit results
                                            break
                        except:
                            continue
                        if search_count > 50:
                            break

                    if results:
                        content = f"Search results for '{pattern}' (showing first 50 matches):\n\n" + "\n".join(results)
                    else:
                        content = f"No matches found for pattern '{pattern}'"

                    return [types.TextContent(type="text", text=content)]

                except Exception as e:
                    return [types.TextContent(type="text", text=f"Error searching for pattern '{pattern}': {str(e)}")]

            elif name == "serena_analyze" and SERENA_AVAILABLE:
                query = arguments.get("query", "")
                context = arguments.get("context", "")

                try:
                    # Basic analysis response - would need to integrate with actual Serena AI
                    result = f"Serena Analysis for query: '{query}'\n"
                    if context:
                        result += f"Context: {context}\n\n"
                    result += "Note: This is a placeholder. Full Serena AI integration would provide detailed code analysis here."

                    return [types.TextContent(type="text", text=result)]

                except Exception as e:
                    return [types.TextContent(type="text", text=f"Error in Serena analysis: {str(e)}")]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            stderr_print(f"Tool error in {name}: {e}")
            return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

    async def main():
        """Run the MCP server"""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await server.run(read_stream, write_stream, server.create_initialization_options())
        except Exception as e:
            stderr_print(f"Server error: {e}")
            sys.exit(1)

    if __name__ == "__main__":
        stderr_print("Starting Serena MCP Server...")
        asyncio.run(main())

except ImportError as e:
    stderr_print(f"MCP library not available: {e}")
    sys.exit(1)
