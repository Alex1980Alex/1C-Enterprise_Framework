"""
Memory MCP Server

MCP (Model Context Protocol) server для интеграции системы долгосрочной памяти с Claude.
Предоставляет tools для сохранения, поиска и восстановления контекста разговоров.
"""

import sys
from pathlib import Path
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Import MCP modules FIRST, before adding local paths
from mcp.server import Server
from mcp import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# NOW add parent directory to path for local service imports
sys.path.insert(0, str(Path(__file__).parent.parent / "services"))

from conversation_storage import ConversationStorage
from message_vectorization import MessageVectorization
from context_restoration import ContextRestoration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory-mcp")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ai_memory',
    'user': 'ai_user',
    'password': 'ai_memory_secure_2025'
}

# Initialize services
storage = ConversationStorage(DB_CONFIG)
vectorizer = MessageVectorization(
    qdrant_host="localhost",
    qdrant_port=6333,
    collection_name="conversation_memory"
)
restoration = ContextRestoration(storage, vectorizer)

# Create MCP server
app = Server("memory-server")

# Global session state
current_session = {
    "session_id": None,
    "conversation_id": None,
    "project_context": None
}


@app.list_tools()
async def list_tools() -> List[Tool]:
    """
    List all available memory tools
    """
    return [
        Tool(
            name="save_conversation_fact",
            description="Save an important fact or message from the current conversation to long-term memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text content to save (message, fact, or important information)"
                    },
                    "importance": {
                        "type": "number",
                        "description": "Importance score from 0.0 to 1.0 (default: 0.5)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5
                    },
                    "role": {
                        "type": "string",
                        "description": "Role of the message sender",
                        "enum": ["user", "assistant", "system"],
                        "default": "assistant"
                    },
                    "has_code": {
                        "type": "boolean",
                        "description": "Whether the content contains code",
                        "default": False
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata (optional)",
                        "default": {}
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="search_memory",
            description="Search for relevant information in long-term memory using semantic and text search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (will use both semantic and text search)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "project_context": {
                        "type": "string",
                        "description": "Filter by project context (optional)"
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum relevance score (0.0-1.0, default: 0.5)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_session_context",
            description="Retrieve relevant context for the current or a specific session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to get context for (uses current session if not specified)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional query to focus the context retrieval"
                    },
                    "max_messages": {
                        "type": "integer",
                        "description": "Maximum number of messages in context (default: 20)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    },
                    "include_semantic": {
                        "type": "boolean",
                        "description": "Include semantically similar messages (default: true)",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="start_memory_session",
            description="Start a new memory session or resume an existing one",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID (generates new if not provided)"
                    },
                    "project_context": {
                        "type": "string",
                        "description": "Project context (e.g., project path or name)"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional session metadata",
                        "default": {}
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_project_summary",
            description="Get a summary of all conversations and important information for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_context": {
                        "type": "string",
                        "description": "Project identifier (uses current project if not specified)"
                    },
                    "include_stats": {
                        "type": "boolean",
                        "description": "Include detailed statistics (default: true)",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_important_messages",
            description="Retrieve the most important messages from memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of messages (default: 10)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "min_importance": {
                        "type": "number",
                        "description": "Minimum importance score (default: 0.7)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.7
                    },
                    "project_context": {
                        "type": "string",
                        "description": "Filter by project (optional)"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """
    Handle tool calls from Claude
    """
    try:
        if name == "save_conversation_fact":
            return await save_conversation_fact(arguments)
        elif name == "search_memory":
            return await search_memory(arguments)
        elif name == "get_session_context":
            return await get_session_context(arguments)
        elif name == "start_memory_session":
            return await start_memory_session(arguments)
        elif name == "get_project_summary":
            return await get_project_summary(arguments)
        elif name == "get_important_messages":
            return await get_important_messages(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def save_conversation_fact(args: Dict) -> List[TextContent]:
    """Save a fact to long-term memory"""

    # Ensure session exists
    if not current_session["conversation_id"]:
        # Auto-create session
        session_id = current_session["session_id"] or f"auto_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        conv_id = storage.create_conversation(
            session_id=session_id,
            project_context=current_session["project_context"] or "default"
        )
        current_session["conversation_id"] = conv_id
        current_session["session_id"] = session_id

    # Save message
    content = args["content"]
    importance = args.get("importance", 0.5)
    role = args.get("role", "assistant")
    has_code = args.get("has_code", False)
    metadata = args.get("metadata", {})

    message_id = storage.add_message(
        conversation_id=current_session["conversation_id"],
        role=role,
        content=content,
        importance_score=importance,
        has_code=has_code,
        metadata=metadata
    )

    # Vectorize for semantic search
    vector_id = vectorizer.vectorize_message(
        message_id=message_id,
        message_timestamp=datetime.utcnow().isoformat(),
        conversation_id=str(current_session["conversation_id"]),
        role=role,
        content=content,
        importance_score=importance,
        metadata=metadata
    )

    return [TextContent(
        type="text",
        text=f"✅ Saved to long-term memory\n"
             f"Message ID: {message_id}\n"
             f"Vector ID: {vector_id}\n"
             f"Importance: {importance}\n"
             f"Session: {current_session['session_id']}"
    )]


async def search_memory(args: Dict) -> List[TextContent]:
    """Search memory using semantic and text search"""

    query = args["query"]
    limit = args.get("limit", 10)
    project_ctx = args.get("project_context", current_session["project_context"])
    min_score = args.get("min_score", 0.5)

    # Perform search
    results = restoration.search_conversation_history(
        query=query,
        project_context=project_ctx,
        limit=limit
    )

    # Filter by score if semantic results
    filtered_results = [
        r for r in results
        if r.get("score", 1.0) >= min_score
    ][:limit]

    if not filtered_results:
        return [TextContent(
            type="text",
            text=f"No results found for query: {query}"
        )]

    # Format results
    result_text = f"🔍 Found {len(filtered_results)} results for: {query}\n\n"

    for i, result in enumerate(filtered_results, 1):
        score = result.get("score", result.get("rank", 0))
        preview = result.get("content_preview", "")
        role = result.get("role", "unknown")

        result_text += f"{i}. [{role}] Score: {score:.3f}\n"
        result_text += f"   {preview[:200]}...\n\n"

    return [TextContent(type="text", text=result_text)]


async def get_session_context(args: Dict) -> List[TextContent]:
    """Get context for current or specific session"""

    session_id = args.get("session_id", current_session["session_id"])
    query = args.get("query")
    max_messages = args.get("max_messages", 20)
    include_semantic = args.get("include_semantic", True)

    if not session_id:
        return [TextContent(
            type="text",
            text="⚠️ No active session. Use start_memory_session first."
        )]

    # Get context
    context = restoration.get_relevant_context(
        query=query,
        project_context=current_session["project_context"],
        session_id=session_id,
        max_messages=max_messages,
        include_semantic=include_semantic
    )

    return [TextContent(
        type="text",
        text=f"📋 Session Context\n"
             f"Session ID: {session_id}\n"
             f"Total messages: {context['total_messages']}\n\n"
             f"{context['context_summary']}"
    )]


async def start_memory_session(args: Dict) -> List[TextContent]:
    """Start or resume a memory session"""

    session_id = args.get("session_id") or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    project_ctx = args.get("project_context", "default")
    metadata = args.get("metadata", {})

    # Create conversation
    conv_id = storage.create_conversation(
        session_id=session_id,
        project_context=project_ctx,
        metadata=metadata
    )

    # Update global state
    current_session["session_id"] = session_id
    current_session["conversation_id"] = conv_id
    current_session["project_context"] = project_ctx

    return [TextContent(
        type="text",
        text=f"✅ Memory session started\n"
             f"Session ID: {session_id}\n"
             f"Conversation ID: {conv_id}\n"
             f"Project: {project_ctx}\n\n"
             f"You can now use save_conversation_fact to save important information."
    )]


async def get_project_summary(args: Dict) -> List[TextContent]:
    """Get project summary"""

    project_ctx = args.get("project_context", current_session["project_context"])
    include_stats = args.get("include_stats", True)

    if not project_ctx:
        return [TextContent(
            type="text",
            text="⚠️ No project context specified"
        )]

    summary = restoration.get_project_summary(
        project_context=project_ctx,
        include_stats=include_stats
    )

    result_text = f"📊 Project Summary: {project_ctx}\n\n"
    result_text += f"Active conversations: {summary['active_conversations']}\n"
    result_text += f"Important messages: {summary['important_messages']}\n"
    result_text += f"Total messages: {summary['total_messages']}\n"

    if include_stats and "global_stats" in summary:
        stats = summary["global_stats"]
        result_text += f"\nGlobal Statistics:\n"
        result_text += f"  Total conversations: {stats.get('total_conversations', 0)}\n"
        result_text += f"  Avg messages/conv: {stats.get('avg_messages_per_conversation', 0):.1f}\n"
        result_text += f"  Avg importance: {stats.get('avg_importance_score', 0):.2f}\n"

    return [TextContent(type="text", text=result_text)]


async def get_important_messages(args: Dict) -> List[TextContent]:
    """Get important messages from memory"""

    limit = args.get("limit", 10)
    min_importance = args.get("min_importance", 0.7)
    project_ctx = args.get("project_context", current_session["project_context"])

    messages = storage.get_important_messages(
        limit=limit,
        min_score=min_importance,
        project_context=project_ctx
    )

    if not messages:
        return [TextContent(
            type="text",
            text=f"No important messages found (min score: {min_importance})"
        )]

    result_text = f"⭐ Top {len(messages)} Important Messages\n\n"

    for i, msg in enumerate(messages, 1):
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        result_text += f"{i}. {role_icon} [{msg['importance_score']:.2f}]\n"
        result_text += f"   {msg['content_preview'][:150]}...\n\n"

    return [TextContent(type="text", text=result_text)]


async def main():
    """Run the MCP server"""
    logger.info("Starting Memory MCP Server...")
    logger.info(f"Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    logger.info(f"Qdrant: localhost:6333")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
