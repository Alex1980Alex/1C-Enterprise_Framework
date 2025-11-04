"""
AI Memory System MCP Server

MCP (Model Context Protocol) сервер для интеграции AI Memory System с Claude Code.

Предоставляет 6 инструментов для интеллектуального поиска по BSL коду.
"""

__version__ = "1.0.0"
__author__ = "Claude Code AI Assistant"

from .server import AIMemoryMCPServer

__all__ = ["AIMemoryMCPServer"]
