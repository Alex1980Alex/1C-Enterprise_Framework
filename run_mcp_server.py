#!/usr/bin/env python3
"""
MCP Server launcher for Serena Framework
Direct stdio implementation
"""

import sys
import os

# Ensure all output goes to stderr except JSON-RPC messages
original_print = print
def stderr_print(*args, **kwargs):
    kwargs['file'] = sys.stderr
    original_print(*args, **kwargs)
    
# Monkey-patch print to redirect to stderr
import builtins
builtins.print = stderr_print

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'serena', 'src'))

# Now import Serena after patching print
from serena.mcp import SerenaMCPFactorySingleProcess
from serena.constants import DEFAULT_CONTEXT, DEFAULT_MODES
from serena.util.logging import MemoryLogHandler
from sensai.util import logging
import logging as stdlogging

if __name__ == "__main__":
    # Configure logging to stderr only
    stdlogging.basicConfig(
        level=stdlogging.INFO,
        stream=sys.stderr,
        format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
    )
    
    # Create MCP server factory
    memory_log_handler = MemoryLogHandler()
    factory = SerenaMCPFactorySingleProcess(
        context=DEFAULT_CONTEXT,
        project=None,
        memory_log_handler=memory_log_handler
    )
    
    # Create and run MCP server
    server = factory.create_mcp_server(
        host="0.0.0.0",
        port=8000,
        modes=DEFAULT_MODES,
        enable_web_dashboard=False,
        enable_gui_log_window=False,
        log_level="INFO",
        trace_lsp_communication=False,
        tool_timeout=None
    )
    
    # Run the server with stdio transport
    server.run(transport="stdio")
