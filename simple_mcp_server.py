#!/usr/bin/env python3
"""
Simple MCP Server for file operations
"""

import sys
import os
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

try:
    from mcp import types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except ImportError as e:
    logger.error(f"MCP library not available: {e}")
    logger.error("Install with: pip install mcp")
    sys.exit(1)

# Create server instance
server = Server("simple-file-server")

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="read_file",
            description="Read contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        types.Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory (default: current directory)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="search_files",
            description="Search for a pattern in files",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Pattern to search for"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in (default: current directory)"
                    },
                    "extensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File extensions to include (e.g., ['.py', '.txt'])"
                    }
                },
                "required": ["pattern"]
            }
        ),
        types.Tool(
            name="file_info",
            description="Get information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file or directory"
                    }
                },
                "required": ["path"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "read_file":
            path = arguments.get("path")
            if not path:
                return [types.TextContent(type="text", text="Error: 'path' parameter is required")]

            try:
                file_path = Path(path)
                if not file_path.exists():
                    return [types.TextContent(type="text", text=f"Error: File '{path}' does not exist")]

                if not file_path.is_file():
                    return [types.TextContent(type="text", text=f"Error: '{path}' is not a file")]

                # Check file size to prevent memory issues (limit to 1MB)
                file_size = file_path.stat().st_size
                if file_size > 1024 * 1024:  # 1MB limit
                    return [types.TextContent(type="text", text=f"Error: File '{path}' is too large ({file_size} bytes). Maximum size is 1MB.")]

                content = file_path.read_text(encoding='utf-8', errors='ignore')
                return [types.TextContent(type="text", text=content)]

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error reading file: {str(e)}")]

        elif name == "write_file":
            path = arguments.get("path")
            content = arguments.get("content", "")

            if not path:
                return [types.TextContent(type="text", text="Error: 'path' parameter is required")]

            try:
                file_path = Path(path)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
                return [types.TextContent(type="text", text=f"Successfully wrote {len(content)} characters to '{path}'")]

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error writing file: {str(e)}")]

        elif name == "list_directory":
            path = arguments.get("path", ".")

            try:
                dir_path = Path(path)
                if not dir_path.exists():
                    return [types.TextContent(type="text", text=f"Error: Directory '{path}' does not exist")]

                if not dir_path.is_dir():
                    return [types.TextContent(type="text", text=f"Error: '{path}' is not a directory")]

                items = []
                for item in sorted(dir_path.iterdir()):
                    if item.is_dir():
                        items.append(f"[DIR]  {item.name}")
                    else:
                        size = item.stat().st_size
                        items.append(f"[FILE] {item.name} ({size} bytes)")

                result = f"Contents of {path}:\n" + "\n".join(items)
                return [types.TextContent(type="text", text=result)]

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error listing directory: {str(e)}")]

        elif name == "search_files":
            pattern = arguments.get("pattern")
            path = arguments.get("path", ".")
            extensions = arguments.get("extensions", [".py", ".txt", ".md", ".json", ".js", ".ts"])

            if not pattern:
                return [types.TextContent(type="text", text="Error: 'pattern' parameter is required")]

            try:
                search_path = Path(path)
                if not search_path.exists():
                    return [types.TextContent(type="text", text=f"Error: Path '{path}' does not exist")]

                results = []
                pattern_lower = pattern.lower()

                # Search in files
                for ext in extensions:
                    for file_path in search_path.rglob(f"*{ext}"):
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            lines = content.splitlines()
                            for i, line in enumerate(lines, 1):
                                if pattern_lower in line.lower():
                                    relative_path = file_path.relative_to(search_path)
                                    results.append(f"{relative_path}:{i}: {line.strip()}")
                                    if len(results) >= 50:  # Limit results
                                        break
                        except:
                            continue

                        if len(results) >= 50:
                            break
                    if len(results) >= 50:
                        break

                if results:
                    result = f"Found {len(results)} matches for '{pattern}':\n" + "\n".join(results)
                else:
                    result = f"No matches found for '{pattern}'"

                return [types.TextContent(type="text", text=result)]

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error searching files: {str(e)}")]

        elif name == "file_info":
            path = arguments.get("path")
            if not path:
                return [types.TextContent(type="text", text="Error: 'path' parameter is required")]

            try:
                file_path = Path(path)
                if not file_path.exists():
                    return [types.TextContent(type="text", text=f"Error: Path '{path}' does not exist")]

                stat = file_path.stat()
                info = [
                    f"Path: {path}",
                    f"Type: {'Directory' if file_path.is_dir() else 'File'}",
                    f"Size: {stat.st_size} bytes",
                    f"Modified: {stat.st_mtime}",
                    f"Created: {stat.st_ctime}",
                ]

                if file_path.is_file():
                    info.append(f"Extension: {file_path.suffix}")

                return [types.TextContent(type="text", text="\n".join(info))]

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error getting file info: {str(e)}")]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Internal error: {str(e)}")]

async def main():
    """Main entry point for the server"""
    logger.info("Starting Simple MCP File Server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)